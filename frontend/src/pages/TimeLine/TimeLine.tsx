import { useParams } from 'react-router-dom';
import { Range } from '../Calendar';
import { isCollitionDateRanges } from '../Calendar';
import { useEffect, useState } from 'react';
import api from '../../api/axios';
import DatePickerOne from '../../components/Forms/DatePicker/DatePickerOne';

type User = {
  user_id: number;
  name: string,
  events: any[];
}

export const HourRangeTable = () => {
  const { groupId } = useParams<{ groupId: string }>();

  const getCurrentWeekRange = () => {
    const today = new Date();
    const currentDay = today.getDay();
    
    // Calcular el inicio de la semana (domingo)
    const startOfWeek = new Date(today);
    startOfWeek.setDate(today.getDate() - currentDay);
    startOfWeek.setHours(0, 0, 0, 0);
  
    // Calcular el final de la semana (sábado)
    const endOfWeek = new Date(today);
    endOfWeek.setDate(today.getDate() + (6 - currentDay));
    endOfWeek.setHours(23, 59, 59, 999);
  
    return { startOfWeek, endOfWeek };
  };
  
  const { startOfWeek, endOfWeek } = getCurrentWeekRange();
  

  const [ users, setUsers ] = useState<User[]>([]);
  const [ hours, setHours ] = useState<number[]>([]);
  const [ filterStartTime, setFilterStartTime ] = useState<Date>(startOfWeek)
  const [ filterEndTime, setFilterEndTime ] = useState<Date>(endOfWeek)

  const hoursBetween = Math.floor((filterEndTime.getTime() - filterStartTime.getTime()) / (1000 * 60 * 60));
  const colors: string[] = ['bg-blue-500','bg-red-500','bg-green-500','bg-yellow-500','bg-purple-500','bg-pink-500','bg-indigo-500','bg-zinc-500','bg-natural-500','bg-stone-500','bg-violet-500','bg-cyan-500','bg-emerald-500'];
  let taskColor: number[] = [];
  let date = filterStartTime;
  let user = 0;

  const fetchTasks = async () => {
    try {
      const response = await api.get(`/agendas/group/${groupId}/${filterStartTime.toISOString()}/${filterEndTime.toISOString()}`);
      setUsers(response.data);
    } catch (error) {
      console.error('Error fetching tasks:', error);
    }
  };

  const handleDateChange = () => {
    if (filterStartTime && filterEndTime) {
      fetchTasks();
    }
  };

  useEffect(() => {
    fetchTasks();
    setHours(renderHours());
  }, []);

  const renderHours = () => {
    const hours = [];
    for (let hour = 0; hour <= hoursBetween; hour++) {
      const formattedHour = (filterStartTime.getHours() + hour) % 24;
      hours.push(formattedHour)
    }
    return hours;
  };
  
  function getColors(index: number) {
    if (index != user) {
      date = filterStartTime
      user = index
    }
    taskColor = []

    const top = new Date(date.getFullYear(), date.getMonth(), date.getDate(), date.getHours() + 1)
    
    users[index].events.map((range, indexRange) => {    
        if (isCollitionDateRanges({
              start_time: date,
              end_time: top,
            }, 
            {
              start_time: new Date(range.start_time), 
              end_time: new Date(range.end_time)
            })
        ) {
          taskColor.push(indexRange)
        }
    })
    
    date = top

    return taskColor.length
  }


  return (
    <div className="overflow-x-auto">
      <div className="max-w-full overflow-x-auto">
        <div className="flex mb-6">
          <label className="mt-3 mr-5 text-black dark:text-white">
            Filter Start Time
          </label>
          <DatePickerOne date={new Date(filterStartTime.getFullYear(), filterStartTime.getMonth(), filterStartTime.getDate(), filterStartTime.getHours() - 5, filterStartTime.getMinutes()).toISOString().slice(0,16)} set={setFilterStartTime}/>
        </div>
        <div className="flex mb-6">
          <label className="mt-3 mr-5 text-black dark:text-white">
            Filter End Time
          </label>
          <DatePickerOne date={new Date(filterEndTime.getFullYear(), filterEndTime.getMonth(), filterEndTime.getDate(), filterEndTime.getHours() - 5, filterEndTime.getMinutes()).toISOString().slice(0,16)} set={setFilterEndTime}/>
        </div>
        <button onClick={() => handleDateChange()} className="flex w-full justify-center rounded bg-primary p-3 font-medium text-gray hover:bg-opacity-90 m-5">
          Filtrar
        </button>
      </div>
      
      <table className="min-w-full bg-white shadow-md rounded-lg overflow-hidden">
        <thead className="bg-gray-50">
          <tr>
            <th className="px-4 py-2 text-left">Hour</th>
            {hours.map((hour, indexHours) => (
              <th key={indexHours} className="px-4 py-2 text-center">{hour}:00</th>
            ))}
          </tr>
        </thead>
        <tbody>
          {users.map((user, userIndex) => (
            <tr key={user.user_id || userIndex}>
              <td className="border px-4 py-2 text-center">{user.name}</td>
              {hours.map(hour => (
                <td key={`${user.user_id || userIndex}-${hour}`} className={`border text-center grid-fils-${getColors(userIndex)}`}>
                  {taskColor.map(i => (
                    <div key={`${user.user_id || userIndex}-${hour}-${i}`} className={`${colors[i]} h-4`}></div>
                  ))}
                </td>
              ))}
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
};

export default HourRangeTable;