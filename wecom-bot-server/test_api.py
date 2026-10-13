import requests
import json

def test_backend_api():
    """测试后端API"""
    print("测试后端API...")
    url = "http://localhost:8002/api/v1/login"
    data = {"username": "admin", "password": "admin123"}
    
    try:
        response = requests.post(url, json=data)
        print(f"状态码: {response.status_code}")
        print(f"响应: {response.json()}")
        return response.status_code == 200
    except Exception as e:
        print(f"错误: {e}")
        return False

def test_frontend_proxy():
    """测试前端代理"""
    print("\n测试前端代理...")
    url = "http://localhost:3001/api/v1/login"
    data = {"username": "admin", "password": "admin123"}
    
    try:
        response = requests.post(url, json=data)
        print(f"状态码: {response.status_code}")
        print(f"响应: {response.json()}")
        return response.status_code == 200
    except Exception as e:
        print(f"错误: {e}")
        return False

def test_frontend_page():
    """测试前端页面"""
    print("\n测试前端页面...")
    url = "http://localhost:3001/"
    
    try:
        response = requests.get(url)
        print(f"状态码: {response.status_code}")
        print(f"内容长度: {len(response.text)}")
        return response.status_code == 200
    except Exception as e:
        print(f"错误: {e}")
        return False

if __name__ == "__main__":
    print("=== 系统测试 ===")
    
    # 测试后端API
    backend_ok = test_backend_api()
    
    # 测试前端代理
    proxy_ok = test_frontend_proxy()
    
    # 测试前端页面
    frontend_ok = test_frontend_page()
    
    print("\n=== 测试结果 ===")
    print(f"后端API: {'✅ 通过' if backend_ok else '❌ 失败'}")
    print(f"前端代理: {'✅ 通过' if proxy_ok else '❌ 失败'}")
    print(f"前端页面: {'✅ 通过' if frontend_ok else '❌ 失败'}")
    
    if backend_ok and proxy_ok and frontend_ok:
        print("\n🎉 所有测试通过！系统正常运行。")
        print("访问地址: http://localhost:3001")
        print("登录账号: admin / admin123")
    else:
        print("\n⚠️ 部分测试失败，请检查服务状态。")