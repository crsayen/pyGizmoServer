module.exports = {
  publicPath: '',
  runtimeCompiler: true,
  devServer: {
    proxy: {
      '^/': {
        target: 'http://localhost:36364/'
      },
      '^/ws/': {
        target: 'http://localhost:11111/'
      }
    }
  }
}
