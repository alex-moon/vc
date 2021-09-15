const webpack = require('webpack');
const path = require('path');

module.exports = {
  entry: './app/ts/vc.ts',
  devtool: 'inline-source-map',
  output: {
    path: path.resolve(__dirname, 'public/assets/js'),
    filename: 'vc.js',
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
  plugins: [
    new webpack.DefinePlugin({
      "typeof window": JSON.stringify("object")
    })
  ],
  module: {
    rules: [
      { test: /\.m?js/, resolve: { fullySpecified: false } },
      { test: /\.scss$/, use: 'sass-loader' },
      { test: /\.ts$/, use: 'ts-loader' },
    ],
  },
  mode: 'development',
};
