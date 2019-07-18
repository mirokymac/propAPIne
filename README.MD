# propAPIne

A restful warpper for COOLPROP thermodynamic library.

Combinate with built-in APP SCRIPT to use NIST.REFPROP like functions in  GOOGLE Sheet.

Thanks @ian bell for bring [COOLPROP](https://github.com/github/gitignore/blob/master/Fortran.gitignore) to us.

## Deployment

### Basic deployment

1. Install Python3 on your hosting machine.

2. Install require packages:

`pip install -y CoolProp flask flask-restful`

3. Clone this respository:

`git clone https://github.com/mirokymac/propAPIne.git`

4. Get into the Server directory to run app.py:

`cd ./propAPIne/server && python3 app.py`

5. Expose port `22001` to client

6. Using restful API client to connext to `HOST:22001`

### Docker deployment

1. Clone this respository:

`git clone https://github.com/mirokymac/propAPIne.git`

2. Build docker image of the server and copy the docker-ID:

`cd ./propAPIne/server_docker && docker build .`

3. Run docker:

`cd .. && docker run -p 22001:22001 {docker-ID}`

4. Expose port `22001` to client

5. Using restful API client to connext to `HOST:22001`

## Enable REFPROP support

Thanks @ian bell again for CoolProp-REFPROP_backend and [REFPROP-cmake](https://github.com/usnistgov/REFPROP-cmake)

1. Clone this respository:
`cd ~ && git clone https://github.com/mirokymac/propAPIne.git`

2. Copy `FORTRAN` directory to `./propAPIne/refprop_builder_docker`.

3. Make a directory `build` in `./propAPIne/refprop_builder_docker`.

4. Build REFPROP by:
`cd ~/propAPIne/refprop_builder_docker && docker build .`

then copy the docker-ID:
`docker run -v $PWD/FORTRAN:/root/REFPROP-cmake/fortran -v $PWD/build:/root/REFPROP-cmake/build {docker-ID}`

5. copy `build/librefprop.so` to `refprop\` of your "server" directory;

6. copy `fuilds` and `mixtures` directories from `NIST_REFPROP` to `refprop\`.

7. Restart your server.

** For docker, you need to link the `refprop` directory to your workdir.
