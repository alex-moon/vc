const path = require('path');

module.exports = {
  entry: {
    'vc': ['./app/ts/elements.ts', './app/ts/vc.ts'],
  },
  devtool: 'inline-source-map',
  output: {
    path: path.resolve(__dirname, 'public/assets/js'),
    filename: '[name].js',
    // filename: 'vc.js',
  },
  watch: true,
  devServer: {
    static: {
      directory: path.resolve(__dirname, 'public'),
    },
    historyApiFallback: {
      index: 'index.html'
    }
  },
  resolve: {
    alias: {
      components: path.resolve(__dirname, 'app'),
    },
    extensions: ['.ts', '.tsx', '.js', '.jsx'],
  },
  module: {
    rules: [
      { test: /\.m?js/, resolve: { fullySpecified: false } },
      { test: /\.scss$/, use: 'sass-loader' },
      { test: /\.ts$/, use: 'ts-loader' },
    ],
  },
  mode: 'development',
};
