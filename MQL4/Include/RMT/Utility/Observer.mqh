#property strict

// 3rdparty
#include <Mql/Collection/Vector.mqh>

/// Receives notifications of a subject.
template <typename T>
interface Observer {
    void on_notify(const T& event);
};

/// Notifies observers of a subject.
template <typename T>
class Subject {
public:
    Subject();
    ~Subject();

    void register(Observer<T>* observer);
    void notify(const T& event);

private:
    Vector<Observer<T>*> m_observers;
};

//===========================================================================
// --- Subject implementation ---
//===========================================================================
template <typename T>
Subject::Subject()
{}

template <typename T>
Subject::~Subject()
{
    foreachv(Observer<T>*, observer, m_observers)
        delete observer;
}

template <typename T>
void Subject::register(Observer<T>* observer)
{
    if (observer != NULL)
        m_observers.add(observer);
}

template <typename T>
void Subject::notify(const T& event)
{
    foreachv(Observer<T>*, observer, m_observers)
        observer.on_notify(event);
}