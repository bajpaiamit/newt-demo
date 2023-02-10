 #!/bin/bash


current_date=$(date -d "yesterday" '+%Y-%m-%d')
#current_date=$(date -d "2 days ago" '+%Y-%m-%d' )
file=$FILE_PROCESS
echo "hello there $file"
#file=$(echo $full_file_path | sed 's@.*/\(.*\)\..*@\1@')

gsutil cp gs://$SECRET_FILE_PATH Secret.gpg

DECRYPT_PASSPHRASE=$(gcloud secrets versions access $DECRYPT_SECRET_VERSION --secret="$DECRYPT_SECRET_ID")

gpg --pinentry-mode=loopback --batch --passphrase $DECRYPT_PASSPHRASE --import Secret.gpg

mkdir ./source_$current_date
mkdir ./zipped_$current_date

set -e

echo `ls -l`
gsutil -m  cp gs://$file source_$current_date/
cd ./source_$current_date
echo `ls -l`
file_name=$(echo "$file" | sed 's/.*\///')

echo $file_name


gpg --pinentry-mode=loopback --batch --passphrase $DECRYPT_PASSPHRASE -d -o ../zipped_$current_date/${file_name%.*}  -d $file_name


cd ..

cd zipped_$current_date

unzip ${file_name%.*} -d $(echo "$file_name" | awk -F . '{print $1}')
gsutil -m  cp -r $(echo "$file_name" | awk -F . '{print $1}') gs://$BUCKET_NAME/Uncompressed_folders/${current_date}/
rm -f ${file_name%.*}
rm -rf $(echo "$file_name" | awk -F . '{print $1}')


