# obsolete solution -> discovered a better one (that actually works :P)

[to follow the chronical order start reading at the nc-downloader section]

After checking the downloads I discovered that while the JPEGs open without any problem my RAW files didn't. Looking closer at the JPEGs I could see that in the last pixel line there were some blocks missing. So the download wasn't finished. Following up on the error message that gets displayed in Nextcloud in the `hasSignature()` call of `splitMetaData()` I discovered that the encrypted data field was empty and therefore there can't be a signature in the file. To bypass this I have added following if clause into the function `symmetricDecryptFileContent()` in `apps/encryption/lib/Crypto/Crypt.php`:

                if ($keyFileContents == '') {
                        return '';
                }

I have put this code as the first command in the `symmetricDecryptFileContent()`. Together with disabling the signature check (putting `return true;` in the `checkSignature()` function in the same file):

```
    private function checkSignature($data, $passPhrase, $expectedSignature) {
            $signature = $this->createSignature($data, $passPhrase);
            if (!hash_equals($expectedSignature, $signature)) {
                    return true;
                    throw new GenericEncryptionException('Bad Signature', $this->l->t('Bad Signature'));
            }
    }
```
I can now see the previews in the web interface and download all files decrypted and even download the folders as zip-files. My script is not necessary anymore :smiley:

# nc-downloader

Downloader for files on Nextcloud.

This script can be used in some cases to recover files with malformed signature after switching off the encryption of Nextcloud, changing files manually and scanning with occ command.

## What did I do wrong?
1. I switched off the encryption without doing a decrypt:all
2. I renamed a folder that was uploaded to the Nextcloud server directly on the disk and rescanned the files with the occ command
3. All files in the renamed folder were changed but the encryption information wasn't updated => signature check for decryption fails

## How did I recover?
First I had to change parts of the Nextcloud source code in a way that the signature check will always return true:

apps/encryption/lib/Crypto/Crypt.php

        /**
         * check for valid signature
         *
         * @param string $data
         * @param string $passPhrase
         * @param string $expectedSignature
         * @throws GenericEncryptionException
         */
        private function checkSignature($data, $passPhrase, $expectedSignature) {
                $signature = $this->createSignature($data, $passPhrase);
                if (!hash_equals($expectedSignature, $signature)) {
                        return true;
                        throw new GenericEncryptionException('Bad Signature', $this->l->t('Bad Signature'));
                }
        }

Unfortunately the server does deliver a different file size and finishes off the download before the client. Every WebDav client and browser will now complain about a connection loss, even though the file was downloaded completely. This error also blocks using the folder download in the web interface. Instead of using wget (would work but needs the direct download link including the secret to authorize the download) or curl (using WebDav and parse all the folders in a bash script with sed/grep) I decided to write a small python script that connects to the server via WebDav.

I am using https://pypi.org/project/webdavclient/ to do all the WebDav processing as it is a very easy to use WebDav API. The pull function of the module allows to download a complete folder instead of only one file and also checks if there are already existing files in the folder that the client doesn't have to download anymore. This function will still fail with an exception due to the "connection loss" but by looping the call and catching the exception this can be bypassed. Even though it is a very dirty hack it is better than not having the files at all :) Just make sure to have a stable connection to the server.
