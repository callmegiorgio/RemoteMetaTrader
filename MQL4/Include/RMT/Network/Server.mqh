#property strict

// 3rdparty
#include <Zmq/Zmq.mqh>
#include <Zmq/Errno.mqh>

// Local
#include "ServerSocket.mqh"

/// TODO
class Server {
public:
    /// Time in milliseconds to wait for a request while on Strategy Tester.
    static const uint RECV_WAIT_TIMEOUT;

    Server(string shared_name = "__RMT_Exp3rt_;D__");

    ~Server();

    bool run(string protocol, string hostname, int rep_port, int pub_port);

    void stop();
    
    ////////////////////////////////////////////////////////////////////////////////
    /// Receives a request on the REP socket.
    ///
    /// If a request that was sent by a client is pending on the REP socket's queue,
    /// pops that request from the queue into `request` and returns `true`.
    ///
    /// Otherwise, if `should_wait` is `true`, waits until a request is received or
    /// until `RECV_WAIT_TIMEOUT` milliseconds have elapsed. If timeout is reached,
    /// or if `should_wait` is `false`, returns `false`. Otherwise, writes the
    /// received request into `request` and returns `true`.
    ///
    /// @param request Destination where the received request is written to.
    /// @param should_wait Whether to wait for a request to be received.
    /// @return `true` if a request was received, and `false` otherwise.
    ///
    ////////////////////////////////////////////////////////////////////////////////
    bool recv_request(string& request, bool should_wait = false);

    bool send_response(string response);

    bool publish_event(string event);

private:
    static int last_error_number();
    static string last_error_message();

    bool start_rep_socket(string addr);
    bool start_pub_socket(string addr);

    void stop_rep_socket();
    void stop_pub_socket();

    Context m_ctx;
    ServerSocket m_rep_socket;
    ServerSocket m_pub_socket;
};

//===========================================================================
// --- Server implementation ---
//===========================================================================
static const uint Server::RECV_WAIT_TIMEOUT = 10;

int Server::last_error_number()
{
    return Zmq::errorNumber();
}

string Server::last_error_message()
{
    return Zmq::errorMessage(Zmq::errorNumber());
}

Server::Server(string shared_name)
    : m_ctx(shared_name)
    , m_rep_socket(m_ctx, ZMQ_REP)
    , m_pub_socket(m_ctx, ZMQ_PUB)
{
    m_ctx.setBlocky(false);
}

Server::~Server()
{
    stop();
    m_ctx.shutdown();
    m_ctx.destroy(0);
}

bool Server::run(string protocol, string hostname, int rep_port, int push_port)
{
    const string rep_addr = StringFormat("%s://%s:%d", protocol, hostname, rep_port);
    const string push_addr = StringFormat("%s://%s:%d", protocol, hostname, push_port);

    return start_rep_socket(rep_addr) && start_pub_socket(push_addr);
}

bool Server::start_rep_socket(string addr)
{
    if (!m_rep_socket.bind(addr))
    {
        PrintFormat("Could not bind (REP) socket to address '%s': %s", addr, last_error_message());
        return false;
    }

    if (!m_rep_socket.set_send_high_water_mark(1))
    {
        Print("Failed to set Send High Water Mater on (REP) socket");
        return false;
    }

    if (!m_rep_socket.set_linger(0))
    {
        Print("Failed to set linger on (REP) socket");
        return false;
    }

    if (!m_rep_socket.set_recv_timeout(RECV_WAIT_TIMEOUT))
    {
        Print("Failed to set receive timeout on REP socket");
        return false;
    }

    Print("Listening for incoming requests on (REP) socket: ", m_rep_socket.address());
    return true;
}

bool Server::start_pub_socket(string addr)
{
    if (!m_pub_socket.bind(addr))
    {
        PrintFormat("Could not bind (PUB) socket to address '%s': %s", addr, last_error_message());
        return false;
    }

    Print("Ready to send events on (PUB) socket: ", m_pub_socket.address());
    return true;
}

void Server::stop()
{
    stop_rep_socket();
    stop_pub_socket();
}

void Server::stop_rep_socket()
{
    if (!m_rep_socket.is_bound())
        return;
    
    Print("Unbinding (REP) socket from address: ", m_rep_socket.address());

    if (!m_rep_socket.unbind())
        Print("Failed to unbind (REP) socket: ", last_error_message());
}

void Server::stop_pub_socket()
{
    if (!m_pub_socket.is_bound())
        return;

    Print("Unbinding (PUB) socket from address: ", m_pub_socket.address());

    if (!m_pub_socket.unbind())
        Print("Failed to unbind (PUB) socket: ", last_error_message());
}

bool Server::recv_request(string& request, bool should_wait)
{
    const int flags = should_wait ? 0 : ZMQ_DONTWAIT;

    if (m_rep_socket.recv(request, flags))
        return true;

    if (last_error_number() != EAGAIN)
        Print("Could not receive request on (REP) socket: ", last_error_message());

    return false;
}

bool Server::send_response(string response)
{
    if (!m_rep_socket.send(response))
    {
        Print("Could not send response on (REP) socket: ", last_error_message());
        return false;
    }

    return true;
}

bool Server::publish_event(string event)
{
    if (m_pub_socket.send(event, ZMQ_DONTWAIT))
        return true;

    if (last_error_number() != EAGAIN)
        Print("Could not publish request on (PUB) socket: ", last_error_message());

    return false;
}