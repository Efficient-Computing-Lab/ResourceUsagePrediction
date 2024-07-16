echo "###############################"
echo "Forecasting Build"
echo "###############################"
read -p "Add version (for example v1.0): " version

docker build -f Dockerfile -t forecasting:$version .

