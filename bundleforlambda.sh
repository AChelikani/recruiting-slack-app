mkdir lambda-recruitbot
cp -R clients/ lambda-recruitbot/clients
cp -R config/ lambda-recruitbot/config
cp -R utils/ lambda-recruitbot/utils
cp -R services/ lambda-recruitbot/services
cp lambda_function.py lambda-recruitbot/
cp -R venv/lib/python3.8/site-packages/ lambda-recruitbot
cd lambda-recruitbot
zip -r -D lambda-recruitbot.zip *
mv lambda-recruitbot.zip ../
cd ..
rm -rf lambda-recruitbot
