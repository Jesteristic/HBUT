#!/usr/bin/env python
"""
Flask应用启动脚本
"""
import sys
import os

sys.path.append(os.path.join(os.path.dirname(__file__), 'backend'))

from web import app

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
