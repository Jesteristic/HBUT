import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'

// build 输出到后端 static 目录下，这样 Flask 可以直接提供
export default defineConfig({
  plugins: [vue()],
  build: {
    outDir: '../static/dist',
    emptyOutDir: true,
    rollupOptions: {
      input: 'src/main.js'
    }
  },
  server: {
    port: 3000
  }
})
