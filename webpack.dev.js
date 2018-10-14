const ConnectHistoryApiFallback = require('connect-history-api-fallback');
const HardSourcePlugin = require('hard-source-webpack-plugin');
const HtmlPlugin = require('html-webpack-plugin');
const path = require('path');

const webpack = require('webpack');

const BASE = path.join(__dirname, 'binah', 'apps', 'image_search');
const SOURCE = path.join(BASE, 'src');

module.exports = {
  entry: [path.join(SOURCE, 'scripts', 'index.ts')],
  mode: 'development',
  plugins: [
    new HtmlPlugin({
      template: path.join(SOURCE, 'index.html'),
      inject: 'body',
    }),
    new HardSourcePlugin({
      info: {
        level: 'info',
        mode: 'none',
      },
    }),
    new webpack.HotModuleReplacementPlugin(),
  ],
  devtool: 'inline-source-map',
  devServer: {
    hot: true,
    historyApiFallback: true,
    inline: true,
    contentBase: SOURCE,
    port: process.env.PORT || 9080,
  },
  resolve: {
    extensions: ['.ts', '.js'],
  },
  module: {
    rules: [
      {
        test: /\.ts$/,
        include: path.join(SOURCE, 'scripts'),
        use: [
          {
            loader: 'thread-loader',
            options: {
              workerParallelJobs: 50,
              workerNodeArgs: ['--max-old-space-size=1024'],
              poolTimeout: Infinity,
              poolParallelJobs: 50,
            },
          },
          {
            loader: 'ts-loader',
            options: {
              happyPackMode: true,
              configFile: path.resolve('tsconfig.json'),
              logLevel: 'info',
            },
          },
        ],
      },
      {
        test: /\.scss$/,
        use: [
          'style-loader',  // creates style nodes from JS strings
          'css-loader',    // translates CSS into CommonJS
          'sass-loader',   // compiles Sass to CSS, using Node Sass by default
        ],
      },
      {
        test: /\.(png|jpg|gif|svg)$/,
        use: 'file-loader',
      },
    ],
  },
};
