import {defineConfig} from 'vite'
import vue from '@vitejs/plugin-vue'

// build 输出到后端 static 目录下，这样 Flask 可以直接提供
export default defineConfig({
  plugins: [vue()],
  build: {
    outDir: '../static/dist',
      emptyOutDir: true
  },
  server: {
      host: '0.0.0.0',
      port: 3000,
      proxy: {
          '/api': {
              target: 'http://localhost:5000',
              changeOrigin: true,
              secure: false,
              configure: (proxy, options) => {
                  proxy.on('proxyReq', (proxyReq, req, res) => {
                      proxyReq.setHeader('Cookie', req.headers.cookie || '');
                  });
              }
          }
      },
      historyApiFallback: true
  }
})
