const path = require('path');
const webpack = require('webpack');
const HtmlWebpackPlugin = require("html-webpack-plugin");
const CopyWebpackPlugin = require("copy-webpack-plugin");

function getEnv() {
  const env = process.env.NODE_ENV || 'public';
  switch (env) {
    case 'private':
      return {
        useLocal: false,
        host: '"https://vc-api.ajmoon.uk"',
      }
    case 'local':
      return {
        useLocal: false,
        host: '"https://vc-api.ajmoon.uk"',
      }
    case 'public':
    default:
      return {
        useLocal: true,
        host: '""',
      }
  }
}

module.exports = {
  entry: {
    'vc': [
      './app/scss/vc.scss',
      './app/ts/elements.ts',
      './app/ts/vc.ts'
    ],
  },
  devtool: 'inline-source-map',
  output: {
    path: path.resolve(__dirname, 'public'),
    filename: '[name].js',
  },
  devServer: {
    static: {
      directory: path.resolve(__dirname, 'public'),
    },
    port: 8000,
    proxy: {
      '/api': {
        target: 'https://vc.ajmoon.uk',
        secure: false,
        changeOrigin: true,
      },
    },
  },
  resolve: {
    alias: {
      components: path.resolve(__dirname, 'app'),
    },
    extensions: ['.ts', '.tsx', '.js', '.jsx'],
  },
  module: {
    rules: [
      {
        test: /\.m?js/,
        resolve: {
          fullySpecified: false
        }
      },
      {
        test: /\.scss$/,
        use: [
            "style-loader",
            "css-loader",
            "sass-loader"
        ]
      },
      {
        test: /\.ts$/,
        use: 'ts-loader'
      },
    ],
  },
  mode: 'development',
  plugins: [
    new HtmlWebpackPlugin({
      inject: "body",
      template: "./app/index.html",
      filename: "index.html"
    }),
    new CopyWebpackPlugin({
      patterns: [
          {
            from: "./app/assets",
            to: "./assets"
          }
      ]
    }),
    new webpack.DefinePlugin({
        'window.env': getEnv(),
    }),
  ]
};
