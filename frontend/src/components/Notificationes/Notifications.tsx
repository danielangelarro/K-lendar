import {useState} from 'react';

type Notification = {
  id: number; 
  title: string;
  description: string;
  date: string;
}

type props = {
  items: Notification[];
}

const NotificationsPage = ({items}: props) => {
  const [ notifications, setNotifications ] = useState(items = [
    {
      id: 0,
      title: 'hola',
      description: 'string',
      date: 'date',
    },
    {
      id: 1,
      title: 'hola1',
      description: 'string1bfgyshjfjhsyufvbjf vf afjfh hkjh h;h v  ',
      date: 'date1',
    },
  ])

  function selection(sel: boolean, id: number) {
    if (sel) {

    }
    
    setNotifications(notifications.filter(not => id != not.id))
  }

  return (
    <div className="container mx-auto px-4 py-8">
      <h2 className="text-3xl font-bold mb-6">Notificationes</h2>
      <ul className="space-y-8">
        {notifications.map((item, index) => (
          <li key={index} className="flex items-center space-x-4">
            <span className="w-2 h-2 bg-gray-300 rounded-full mr-3"></span>
            <div className='border p-2 w-full'>
              <p className="font-semibold text-lg">{item.title}</p>
              <p className="text-sm text-gray-600">{item.description}</p>
              <div className='flex'>
                <button className='inline-flex items-center rounded font-medium m-4 px-10 py-4 justify-center bg-blue-500 w-24 h-8 p-2 hover:bg-opacity-90 lg:px-8 xl:px-10' onClick={() => selection(true, item.id)}>Accept</button>
                <button className='inline-flex items-center rounded font-medium m-4 px-10 py-4 justify-center bg-blue-500 w-24 h-8 p-2 hover:bg-opacity-90 lg:px-8 xl:px-10' onClick={() => selection(false, item.id)}>Delete</button>
              </div>
            </div>
          </li>
        ))}
      </ul>
    </div>
  );
};

export default NotificationsPage;