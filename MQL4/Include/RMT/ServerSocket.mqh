#property strict

// 3rdparty
#include <Zmq/Zmq.mqh>

class ServerSocket : private Socket {
public:
    ServerSocket(Context& context, int socket_type);
    
    void connect(string address);
    void disconnect();
    bool is_connected() const;
    
    string recv();
    bool send(string message);

private:
    string address_;
};

//===========================================================================
// --- ServerSocket implementation ---
//===========================================================================
ServerSocket::ServerSocket(Context& context, int socket_type)
    : Socket(context, socket_type)
{}

void ServerSocket::connect(string address)
{
    if (is_connected())
        disconnect();
    
    if (bind(address))
    {
        setSendHighWaterMark(1);
        setLinger(0);

        address_ = address;
    }
}

void ServerSocket::disconnect()
{
    if (!is_connected())
        return;
    
    if (unbind(address_))
        address_ = string();
}

bool ServerSocket::is_connected() const
{
    return address_ != string();
}

string ServerSocket::recv()
{
    ZmqMsg zmq_msg;
    
    if (!Socket::recv(zmq_msg, true))
        return NULL;

    return zmq_msg.getData();
}

bool ServerSocket::send(string message)
{
    return Socket::send(message, true);
}