minimal-sec
===========

Practical for securing communications between server and client.


##ToDo
- [X] Add both TCP and UDP handler
- [X] Minimal client that can connect to server
- [X] Fix server
- [X] Entity authentication protocol
- [X] Protocol for file transfer
- [X] Setup config file in server
- [X] Improve entity authentication by using passphrases. Write libray to collect large corpus that gets updated regularly
- [X] Send email
- [X] Fix ascci encoding error with passphrases
- [X] Setup file storage in server
- [X] Setup nonces
- [X] Fix encryption in 3way handshake
- [X] Server should verify recieved file validity
- [ ] Build UI for the client
- [ ] add email attachments
- [ ] cleanup cc issue in email
- [ ] cleanup file storage to be able to push folders in server
- [X] keyexchange between client and server for encrypting files
- [X] Verify correctness of padding scheme in security
- [X] support long body in email
- [ ] initialisation vector in security.encrypt() only supports AES block sizes
- [ ] Client request file details from server
- [ ] Exchange master key

##Deprecated
- UDP support
- Server cannot decrypt files
