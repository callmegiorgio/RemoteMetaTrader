#property strict

// 3rdparty
#include <Zmq/Zmq.mqh>

class ServerSocket {
public:
    ServerSocket(Context& context, int socket_type);
    
    bool bind(string addr);
    bool unbind();
    bool is_bound() const;

    bool set_send_high_water_mark(int hwm);
    bool set_recv_high_water_mark(int hwm);

    bool set_send_timeout(int timeout = -1);
    bool set_recv_timeout(int timeout = -1);

    bool set_linger(int linger);
    
    bool recv(string& message, int flags = 0);
    bool send(string message, int flags = 0);

    string address() const;

private:
    Socket m_socket;
    string m_address;
};

//===========================================================================
// --- ServerSocket implementation ---
//===========================================================================
ServerSocket::ServerSocket(Context& context, int socket_type)
    : m_socket(context, socket_type)
    , m_address(NULL)
{}

bool ServerSocket::bind(string addr)
{
    if (!unbind())
        return false;

    if (!m_socket.bind(addr))
        return false;
    
    // We attempt to retrieve the bound address by getting the socket option
    // `ZMQ_LAST_ENDPOINT` (or `getLastEndpoint()`), just in case a wildcard
    // IP address, such as "tcp://*:8080", is provided. Note that this call
    // will only work with the TCP and IPC protocols, as per the ZMQ docs.
    // In other words, if the socket is connected on a UDP or another protocol,
    // this function will return `false`. In that case, we'll simply assume
    /// the given `addr` will be understood by `Socket::unbind(addr)`.
    if (!m_socket.getLastEndpoint(m_address))
        m_address = addr;

    return true;
}

bool ServerSocket::unbind()
{
    if (!is_bound())
        return true;

    if (m_socket.unbind(m_address))
    {
        m_address = NULL;
        return true;
    }

    return false;
}

bool ServerSocket::is_bound() const
{
    return m_address != NULL;
}

bool ServerSocket::set_send_high_water_mark(int hwm)
{
    return m_socket.setSendHighWaterMark(hwm);
}

bool ServerSocket::set_recv_high_water_mark(int hwm)
{
    return m_socket.setReceiveHighWaterMark(hwm);
}

bool ServerSocket::set_send_timeout(int timeout)
{
    return m_socket.setSendTimeout(timeout);
}

bool ServerSocket::set_recv_timeout(int timeout)
{
    return m_socket.setReceiveTimeout(timeout);
}

bool ServerSocket::set_linger(int linger)
{
    return m_socket.setLinger(linger);
}

bool ServerSocket::recv(string& message, int flags)
{
    ZmqMsg zmq_msg;

    if (zmq_msg_recv(zmq_msg, m_socket.ref(), flags) == -1)
        return false;

    message = zmq_msg.getData();
    return true;
}

bool ServerSocket::send(string message, int flags)
{
    ZmqMsg zmq_msg(message);

    return zmq_msg_send(zmq_msg, m_socket.ref(), flags) != -1;
}

string ServerSocket::address() const
{
    return m_address;
}