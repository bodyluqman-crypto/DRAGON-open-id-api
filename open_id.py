from http.server import BaseHTTPRequestHandler
import requests
import json
import time
from urllib.parse import urlparse, parse_qs

class handler(BaseHTTPRequestHandler):
    
    def do_GET(self):
        parsed_path = urlparse(self.path)
        path = parsed_path.path
        query = parse_qs(parsed_path.query)
        
        # ===== الصفحة الرئيسية =====
        if path == "/" or path == "":
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            
            response = {
                "success": True,
                "api": "DRAGON OpenID API",
                "version": "1.120.1",
                "build": "OB52",
                "status": "online",
                "endpoints": {
                    "/": "Home page",
                    "/api/openid?uid={UID}": "Get Open ID from UID",
                    "/api/openid?uid={UID}&full=true": "Get full account data"
                },
                "example": "/api/openid?uid=14152363418",
                "documentation": "https://github.com/bodyluqman-crypto/DRAGON-API-OPEN_ID"
            }
            self.wfile.write(json.dumps(response, indent=2).encode())
            return
        
        # ===== API endpoint =====
        if path == "/api/openid":
            uid = query.get('uid', [None])[0]
            full = query.get('full', ['false'])[0].lower() == 'true'
            
            if not uid:
                self.send_response(400)
                self.send_header('Content-type', 'application/json')
                self.send_header('Access-Control-Allow-Origin', '*')
                self.end_headers()
                self.wfile.write(json.dumps({
                    "success": False,
                    "error": "UID is required",
                    "example": "/api/openid?uid=14152363418"
                }).encode())
                return
            
            try:
                # ✅ Garena OAuth API الحقيقي - Version 1.120.1
                url = "https://100067.connect.garena.com/oauth/guest/token/grant"
                
                headers = {
                    "Host": "100067.connect.garena.com",
                    "User-Agent": "GarenaMSDK/4.0.19P4(G011A;Android 9;en;US;)",
                    "Content-Type": "application/x-www-form-urlencoded",
                    "Accept-Encoding": "gzip, deflate, br",
                    "Connection": "close",
                }
                
                data = {
                    "uid": uid,
                    "password": "",
                    "response_type": "token",
                    "client_type": "2",
                    "client_secret": "",
                    "client_id": "100067",
                    "app_version": "1.120.1",
                    "release_version": "OB52"
                }
                
                response = requests.post(url, headers=headers, data=data, timeout=15)
                
                if response.status_code == 200:
                    result = response.json()
                    
                    # استخراج البيانات الحقيقية
                    access_token = result.get('access_token')
                    open_id = result.get('open_id')
                    account_id = result.get('account_id')
                    region = result.get('region', 'Unknown')
                    nickname = result.get('account_name', 'Unknown')
                    platform = result.get('platform', 4)
                    
                    if open_id:
                        response_data = {
                            "success": True,
                            "uid": uid,
                            "open_id": open_id,
                            "account_id": account_id,
                            "nickname": nickname,
                            "region": region,
                            "platform": "Android" if platform == 4 else "iOS",
                            "version": "1.120.1",
                            "build": "OB52",
                            "timestamp": int(time.time())
                        }
                        
                        # إذا طلب بيانات كاملة
                        if full and access_token:
                            response_data["access_token"] = access_token
                            response_data["token_expires"] = int(time.time()) + 3600
                        
                        self.send_response(200)
                        self.send_header('Content-type', 'application/json')
                        self.send_header('Access-Control-Allow-Origin', '*')
                        self.end_headers()
                        self.wfile.write(json.dumps(response_data, indent=2).encode())
                    else:
                        self.send_response(404)
                        self.send_header('Content-type', 'application/json')
                        self.send_header('Access-Control-Allow-Origin', '*')
                        self.end_headers()
                        self.wfile.write(json.dumps({
                            "success": False,
                            "error": "Open ID not found for this UID",
                            "uid": uid,
                            "version": "1.120.1"
                        }).encode())
                else:
                    self.send_response(404)
                    self.send_header('Content-type', 'application/json')
                    self.send_header('Access-Control-Allow-Origin', '*')
                    self.end_headers()
                    self.wfile.write(json.dumps({
                        "success": False,
                        "error": f"Garena API error: {response.status_code}",
                        "uid": uid,
                        "version": "1.120.1"
                    }).encode())
                    
            except Exception as e:
                self.send_response(500)
                self.send_header('Content-type', 'application/json')
                self.send_header('Access-Control-Allow-Origin', '*')
                self.end_headers()
                self.wfile.write(json.dumps({
                    "success": False,
                    "error": str(e),
                    "version": "1.120.1"
                }).encode())
            return
        
        # ===== 404 لأي رابط آخر =====
        self.send_response(404)
        self.send_header('Content-type', 'application/json')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.end_headers()
        self.wfile.write(json.dumps({
            "success": False,
            "error": "Endpoint not found",
            "available": ["/", "/api/openid"]
        }).encode())
    
    def do_OPTIONS(self):
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers()