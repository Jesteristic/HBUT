#!/usr/bin/env python
"""
Flask应用启动脚本
"""
from backend.web import app

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
