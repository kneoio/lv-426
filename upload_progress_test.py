#!/usr/bin/env python3

import requests
import time
import json
import threading
import sys
import os
from pathlib import Path
from dotenv import load_dotenv
import socket
import socketserver
import http.server
from urllib.parse import urlparse

load_dotenv()


class SlowProxyHandler(http.server.BaseHTTPRequestHandler):
    def __init__(self, *args, target_host, target_port, bandwidth_limit, **kwargs):
        self.target_host = target_host
        self.target_port = target_port
        self.bandwidth_limit = bandwidth_limit
        super().__init__(*args, **kwargs)

    def do_POST(self):
        self.proxy_request()

    def do_GET(self):
        self.proxy_request()

    def proxy_request(self):
        try:
            target_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            target_sock.settimeout(30)
            target_sock.connect((self.target_host, self.target_port))

            request_line = f"{self.command} {self.path} HTTP/1.1\r\n"
            target_sock.send(request_line.encode())

            for header, value in self.headers.items():
                if header.lower() not in ['host', 'connection']:
                    target_sock.send(f"{header}: {value}\r\n".encode())
            target_sock.send(f"Host: {self.target_host}:{self.target_port}\r\n".encode())
            target_sock.send(f"Connection: close\r\n".encode())
            target_sock.send(b"\r\n")

            if 'content-length' in self.headers:
                content_length = int(self.headers['content-length'])
                if content_length > 0:
                    print(f"Proxy: Forwarding {content_length} bytes...")
                    self.forward_data_slow(self.rfile, target_sock, content_length)

            response_data = b""
            target_sock.settimeout(5)

            try:
                while True:
                    chunk = target_sock.recv(4096)
                    if not chunk:
                        break
                    response_data += chunk
            except socket.timeout:
                pass

            target_sock.close()

            if response_data:
                self.wfile.write(response_data)
            else:
                self.send_error(500, "No response from server")

        except Exception as e:
            print(f"Proxy error: {e}")
            try:
                self.send_error(500, f"Proxy error: {str(e)}")
            except:
                pass

    def forward_data_slow(self, source, destination, total_bytes):
        bytes_sent = 0
        chunk_size = min(8192, self.bandwidth_limit // 4)

        while bytes_sent < total_bytes:
            remaining = total_bytes - bytes_sent
            to_read = min(chunk_size, remaining)

            chunk = source.read(to_read)
            if not chunk:
                break

            destination.send(chunk)
            bytes_sent += len(chunk)

            time.sleep(len(chunk) / self.bandwidth_limit)

            progress = (bytes_sent / total_bytes) * 100
            if int(progress) % 10 == 0:
                print(f"Proxy: {progress:.0f}% uploaded ({bytes_sent}/{total_bytes} bytes)")

        print(f"Proxy: Upload completed - {bytes_sent} bytes forwarded")

    def log_message(self, format, *args):
        pass


class SlowProxy:
    def __init__(self, target_host, target_port, proxy_port=8888, bandwidth_kbps=50):
        self.target_host = target_host
        self.target_port = target_port
        self.proxy_port = proxy_port
        self.bandwidth_limit = bandwidth_kbps * 1024
        self.server = None
        self.server_thread = None

    def start(self):
        def handler(*args, **kwargs):
            return SlowProxyHandler(*args,
                                    target_host=self.target_host,
                                    target_port=self.target_port,
                                    bandwidth_limit=self.bandwidth_limit,
                                    **kwargs)

        self.server = socketserver.TCPServer(("127.0.0.1", self.proxy_port), handler)
        self.server_thread = threading.Thread(target=self.server.serve_forever, daemon=True)
        self.server_thread.start()
        print(
            f"Proxy started: localhost:{self.proxy_port} -> {self.target_host}:{self.target_port} @ {self.bandwidth_limit // 1024}KB/s")

    def stop(self):
        if self.server:
            self.server.shutdown()
            self.server.server_close()


class UploadTester:
    def __init__(self, use_proxy=False, bandwidth_kbps=50):
        self.base_url = os.getenv('API_HOST').rstrip('/')
        self.session = requests.Session()
        self.proxy = None

        auth_token = os.getenv('API_TOKEN')
        if auth_token:
            self.session.headers.update({'Authorization': f'Bearer {auth_token}'})
        else:
            raise ValueError("API_TOKEN required")

        if not self.base_url:
            raise ValueError("API_HOST required")

        if use_proxy:
            parsed_url = urlparse(self.base_url)
            host = parsed_url.hostname
            port = parsed_url.port or (443 if parsed_url.scheme == 'https' else 80)

            self.proxy = SlowProxy(host, port, bandwidth_kbps=bandwidth_kbps)
            self.proxy.start()
            self.base_url = f"http://127.0.0.1:{self.proxy.proxy_port}"

    def test_upload_with_real_progress(self, file_path, entity_id="temp"):
        upload_url = f"{self.base_url}/api/soundfragments/files/{entity_id}"

        print(f"Testing: {file_path}")
        print(f"Size: {os.path.getsize(file_path) / (1024 * 1024):.2f}MB")
        print("=" * 60)

        upload_result = {'response': None, 'error': None, 'done': False, 'upload_id': None}

        def do_upload():
            try:
                print("Starting upload request...")
                with open(file_path, 'rb') as f:
                    files = {'file': (file_path.name, f, 'audio/wav')}
                    response = self.session.post(upload_url, files=files, timeout=(30, 600))
                    upload_result['response'] = response

                    if response.status_code == 200:
                        data = response.json()
                        upload_result['upload_id'] = data.get('id')
                        print(f"Upload completed - ID: {upload_result['upload_id']}")
                    else:
                        print(f"Upload failed: {response.status_code}")

            except Exception as e:
                upload_result['error'] = e
                print(f"Upload error: {e}")
            finally:
                upload_result['done'] = True

        # Start upload in background
        upload_thread = threading.Thread(target=do_upload, daemon=True)
        upload_thread.start()

        # Wait a moment for upload to start
        time.sleep(1)

        # Monitor for upload ID to become available
        start_time = time.time()
        poll_count = 0

        print("Waiting for upload ID...")
        while not upload_result['done'] and not upload_result['upload_id']:
            poll_count += 1
            elapsed = time.time() - start_time
            print(f"[{poll_count:2d}] {elapsed:5.1f}s - Waiting for server response...")
            time.sleep(2)

        # Once we have upload ID, start monitoring progress
        if upload_result['upload_id']:
            print(f"\nGot upload ID: {upload_result['upload_id']}")
            print("Starting real server progress monitoring...")
            print("=" * 60)

            self.monitor_server_progress(upload_result['upload_id'])

        # Wait for upload to complete
        upload_thread.join()

        # Final result
        if upload_result['error']:
            print(f"FINAL RESULT: ERROR - {upload_result['error']}")
        elif upload_result['response'] and upload_result['response'].status_code == 200:
            print(f"FINAL RESULT: SUCCESS")
        else:
            print(
                f"FINAL RESULT: FAILED - {upload_result['response'].status_code if upload_result['response'] else 'No response'}")

        if self.proxy:
            self.proxy.stop()

    def monitor_server_progress(self, upload_id):
        progress_url = f"{self.base_url}/api/soundfragments/upload-progress/{upload_id}"

        poll_count = 0
        start_time = time.time()
        last_percentage = -1

        while True:
            try:
                poll_count += 1
                elapsed = time.time() - start_time

                response = self.session.get(progress_url)

                if response.status_code == 404:
                    print(f"[{poll_count:2d}] {elapsed:5.1f}s - Server: Upload session not found (404)")
                    break
                elif response.status_code != 200:
                    print(f"[{poll_count:2d}] {elapsed:5.1f}s - Server: HTTP {response.status_code}")
                    try:
                        error_data = response.json()
                        print(f"      Error JSON: {json.dumps(error_data, indent=8)}")
                    except:
                        print(f"      Error Text: {response.text[:200]}")
                    break

                data = response.json()
                status = data.get('status', 'unknown')
                percentage = data.get('percentage', 0)

                # Only show when progress changes or every 10 polls
                if percentage != last_percentage or poll_count % 10 == 1:
                    print(f"[{poll_count:2d}] {elapsed:5.1f}s - Server: {percentage:3d}% - {status}")
                    last_percentage = percentage

                if status in ['finished', 'error']:
                    print("=" * 60)
                    print(f"Server processing completed: {status}")
                    if data.get('metadata'):
                        metadata = data['metadata']
                        print(f"File info: {metadata.get('durationSeconds', '?')}s, {metadata.get('bitRate', '?')} bps")
                    break

                time.sleep(0.5)

            except Exception as e:
                print(f"[{poll_count:2d}] Progress poll error: {e}")
                break


def main():
    try:
        # Use slow proxy to simulate real network conditions
        tester = UploadTester(use_proxy=True, bandwidth_kbps=1000)

        hardcoded_file = Path("C:/Users/justa/Music/Fractured Signals.wav")

        if hardcoded_file.exists():
            tester.test_upload_with_real_progress(hardcoded_file, "temp")
        else:
            print(f"File not found: {hardcoded_file}")

    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()