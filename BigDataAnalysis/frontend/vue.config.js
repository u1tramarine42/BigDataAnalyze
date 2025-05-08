const { defineConfig } = require('@vue/cli-service')
const webpack = require('webpack')

module.exports = defineConfig({
  transpileDependencies: true,
  configureWebpack: {
    plugins: [
      // 提供buffer全局变量的polyfill
      new webpack.ProvidePlugin({
        Buffer: ['buffer', 'Buffer'],
      }),
    ],
    resolve: {
      fallback: {
        // 为Node.js核心模块提供polyfill
        buffer: require.resolve('buffer/'),
        // 不使用的模块设置为false
        fs: false,
        path: false
      }
    }
  }
})
