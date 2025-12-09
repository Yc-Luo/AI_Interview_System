const { defineConfig } = require('@vue/cli-service')

module.exports = defineConfig({
  transpileDependencies: true,
  devServer: {
    port: 8080, // 确保前端跑在 8080 (或者你习惯的端口)
    proxy: {
      '/api': {
        target: 'http://localhost:8000',  // 这里写你的后端地址
        changeOrigin: true,               // 允许跨域
        ws: true,
        // 注意：不要写 pathRewrite，因为你的后端地址里本身就包含 /api
        // 如果你的后端地址是 localhost:8000/activities (没有api前缀)，才需要 pathRewrite
      }
    }
  }
})
