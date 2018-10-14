const CleanPlugin = require('clean-webpack-plugin');
const HtmlPlugin = require('html-webpack-plugin');
const MiniCssExtractPlugin = require('mini-css-extract-plugin');
const UglifyJsPlugin = require('uglifyjs-webpack-plugin');
const CopyWebpackPlugin = require('copy-webpack-plugin');
const path = require('path');

const BASE = path.join(__dirname, 'binah', 'apps', 'image_search');
const SOURCE = path.join(BASE, 'src');
const DIST = path.join(BASE, 'dist');

module.exports = {
  context: SOURCE,
  entry: ['./scripts/index.ts'],
  mode: 'production',
  output: {
    path: DIST,
    filename: 'scripts/[name].[hash].js',
    publicPath: './',
  },
  plugins: [
    new CleanPlugin('dist', {
      root: BASE,
    }),
    new MiniCssExtractPlugin({
      filename: 'styles/[name].[hash].css',
    }),
    new HtmlPlugin({
      template: path.join(SOURCE, 'index.html'),
    }),
    new CopyWebpackPlugin([
      {from: path.join(SOURCE, 'assets'), to: path.join(DIST, 'assets')},
    ]),
  ],
  optimization: {
    minimizer: [
      new UglifyJsPlugin({
        cache: true,
        parallel: true,
        uglifyOptions: {
          compress: {
            drop_console: true,
          },
        },
      }),
    ],
  },
  resolve: {
    extensions: ['.ts', '.js'],
  },
  module: {
    rules: [
      {
        test: /\.scss$/,
        use: [
          {
            loader: MiniCssExtractPlugin.loader,
            options: {
              publicPath: path.join(path.sep),
            },
          },
          {
            loader: 'css-loader',
            options: {
              minimize: true,
            },
          },
          {
            loader: 'thread-loader',
            options: {
              workerParallelJobs: 50,
              poolParallelJobs: 50,
            },
          },
          'sass-loader',
        ],
      },
      {
        test: /\.ts$/,
        include: path.resolve(SOURCE, 'scripts'),
        use: [
          {
            loader: 'thread-loader',
            options: {
              workerParallelJobs: 50,
              poolParallelJobs: 50,
            },
          },
          {
            loader: 'ts-loader',
            options: {
              happyPackMode: true,
              configFile: path.resolve('tsconfig.json'),
            },
          },
        ],
      },
      {
        test: /\.jpg$/,
        loader: 'url-loader',
        options: {limit: 10000, mimetype: 'image/jpg'},
      },
      {
        test: /\.png$/,
        loader: 'url-loader',
        options: {limit: 10000, mimetype: 'image/png'},
      },
      {
        test: /\.svg$/,
        loader: 'url-loader',
        options: {limit: 10000, mimetype: 'image/svg+xml'},
      },
      {
        test: /\.html$/,
        use: [
          {
            loader: 'html-loader',
            options: {
              minimize: true,
            },
          },
        ],
      },
    ],
  },
};
