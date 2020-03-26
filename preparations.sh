echo "Making database migrations..."
python3 manage.py makemigrations
echo "Migrating changes to db.sqlite3..."
python3 manage.py migrate
echo "Collecting static files..."
python3 manage.py collectstatic
echo "Granting access permissions to db.sqlite3..."
sudo chown www-data db.sqlite3
sudo chown www-data ../Leitner/
sudo chmod 664 db.sqlite3
sudo chown :www-data db.sqlite3
sudo chown :www-data ../Leitner/
sudo chmod -R 777 /var/www/
sudo chown -R www-data /var/www/
echo "Restarting Apache2..."
sudo service apache2 restart
echo "done!"
