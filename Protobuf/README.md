# Installation

We use Protocol Buffers v3. If using OS X, execute:

        brew update && brew install protobuf
        pip install requests protobuf

# Run

To run the server, execute:

        make && make run

# Writeup

- Decision to use HTTP as oppose to a raw TCP socket
- Flask, use of endpoints rather than one centralised dispatcher (Protocol Buffers does not have great support for Union types, and messages do not contain descriptions of their own types)
