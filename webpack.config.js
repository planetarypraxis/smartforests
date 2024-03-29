const path = require("path");
const BundleTracker = require("webpack-bundle-tracker");
const MiniCssExtractPlugin = require("mini-css-extract-plugin");
const Dotenv = require('dotenv-webpack')

const isProduction = process.env.NODE_ENV === "production";

/** @type {import("webpack").WebpackOptionsNormalized } */
module.exports = {
  mode: isProduction ? "production" : "development",
  entry: {
    main: [
      "./smartforests/scss/index.scss",
      "./smartforests/typescript/index.tsx"
    ],
  },
  devtool: isProduction ? "eval-source-map" : false,
  resolve: {
    extensions: ['.ts', '.tsx', '.scss', '...']
  },
  module: {
    rules: [
      {
        test: /\.(png|svg|jpg|jpeg|gif|ttf)$/i,
        type: "asset/resource",
      },
      {
        test: /\.(tsx?|jsx?)$/i,
        use: [
          {
            loader: "babel-loader",
          },
        ],
      },
      {
        test: /\.(scss)$/,
        use: [
          {
            // inject CSS to page
            loader: isProduction ? MiniCssExtractPlugin.loader : "style-loader",
          },
          {
            // translates CSS into CommonJS modules
            loader: "css-loader",
          },
          {
            // Run postcss actions
            loader: "postcss-loader",
            options: {
              postcssOptions: {
                plugins: function () {
                  return [require("autoprefixer")];
                },
              },
            },
          },
          {
            loader: "sass-loader",
          },
        ],
      },
      {
        test: /\.(css)$/,
        use: [
          {
            // inject CSS to page
            loader: isProduction ? MiniCssExtractPlugin.loader : "style-loader",
          },
          {
            // translates CSS into CommonJS modules
            loader: "css-loader",
          },
          {
            // Run postcss actions
            loader: "postcss-loader",
            options: {
              postcssOptions: {
                plugins: function () {
                  return [require("autoprefixer")];
                },
              },
            },
          },
        ],
      },
    ],
  },

  devServer: {
    headers: {
      "Access-Control-Allow-Origin": "*",
      "Access-Control-Allow-Methods": "GET, POST, PUT, DELETE, PATCH, OPTIONS",
      "Access-Control-Allow-Headers":
        "X-Requested-With, content-type, Authorization",
    },
  },

  plugins: isProduction ? [
    // Production plugins
    new MiniCssExtractPlugin({
      filename: "[name]-[contenthash].css",
      chunkFilename: isProduction ? "[id]-[hash].css" : "[id].js",
    }),
    new BundleTracker({
      path: __dirname,
      filename: "./dist/webpack-stats.json",
    }),
  ] : [
    // Development plugins
    new Dotenv(),
  ],
  output: {
    filename: isProduction ? "[name]-[hash].js" : "[name].js",
    chunkFilename: isProduction ? "[id]-[hash].js" : "[id].js",
    path: path.resolve(__dirname, "dist"),
    pathinfo: false,
  },
};
