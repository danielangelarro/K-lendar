import {useEffect, useState} from 'react';
import api from '../../api/axios';

interface Notification {
  id: string,
  title: string,
  message: string,
  priority: boolean,
  date: string,
}

type props = {
  items: Notification[];
}

const NotificationsPage = ({items}: props) => {
  const [notifications, setNotifications] = useState<Notification[]>([]);

  const fetchNotifications = async () => {
    try {
      const response = await api.get('/notifications');
      setNotifications(response.data);
    } catch (error) {
      console.error('Error fetching notifications:', error);
    }
  };

  useEffect(() => {
    fetchNotifications();
  }, []);

  function selection(sel: boolean, id: number) {
    if (sel) {

    }
    
    setNotifications(notifications.filter(not => id != not.id))
  }

  return (
    <div className="container mx-auto px-4 py-8">
      <h2 className="text-3xl font-bold mb-6">Notifications</h2>
      <ul className="space-y-8">
        {notifications.map((item, index) => (
          <li key={index} className="flex items-center space-x-4">
            <span className="w-2 h-2 bg-gray-300 rounded-full mr-3"></span>
            <div className='border p-2 w-full'>
              <p className="font-semibold text-lg">Notification</p>
              {/* <p className="font-semibold text-lg">{item.title}</p> */}
              <p className="text-sm text-gray-600">{item.message}</p>

              {( !item.priority &&
                <div className='flex'>
                  <button className='inline-flex items-center rounded font-medium m-4 px-10 py-4 justify-center bg-blue-500 w-24 h-8 p-2 hover:bg-opacity-90 lg:px-8 xl:px-10' onClick={() => selection(true, item.id)}>Accept</button>
                  <button className='inline-flex items-center rounded font-medium m-4 px-10 py-4 justify-center bg-blue-500 w-24 h-8 p-2 hover:bg-opacity-90 lg:px-8 xl:px-10' onClick={() => selection(false, item.id)}>Delete</button>
                </div>
              )}
            </div>
          </li>
        ))}
      </ul>
    </div>
  );
};

export default NotificationsPage;