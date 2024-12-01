import { Range } from '../Calendar';
import { isCollitionDateRanges } from '../Calendar';

type User = {
  id: number;
  taskRange: Range[];
}

type props = {
  startDate: Date;
  endDate: Date;
  ranges: Range[];
  users: User[]
}

const startDate = new Date(2024,10,1,4,59)
const endDate = new Date(2024,10,3,2)

const users: User[] = [
  {
    id: 0,
    taskRange: [
      {
        start_time: new Date(2024,2,3),
        end_time: new Date(2024,2,4),
      },
      {
        start_time: new Date(2024,10,2),
        end_time: new Date(2024,10,3),
      },
      {
        start_time: new Date(2024,10,2),
        end_time: new Date(2024,11,4),
      },
    ],
  },
  {
    id: 1,
    taskRange: [
      {
        start_time: new Date(2024,2,3),
        end_time: new Date(2024,2,4),
      },
      {
        start_time: new Date(2024,10,2),
        end_time: new Date(2024,10,3),
      },
      {
        start_time: new Date(2024,10,2),
        end_time: new Date(2024,11,4),
      },
    ],
  },
  {
    id: 2,
    taskRange: [
      {
        start_time: new Date(2024,2,3),
        end_time: new Date(2024,2,4),
      },
      {
        start_time: new Date(2024,10,2),
        end_time: new Date(2024,10,3),
      },
      {
        start_time: new Date(2024,10,2),
        end_time: new Date(2024,11,4),
      },
    ],
  },
]

export const HourRangeTable = () => {
  const hoursBetween = Math.floor((endDate.getTime() - startDate.getTime()) / (1000 * 60 * 60));
  const colors: string[] = ['bg-blue-500','bg-red-500','bg-green-500','bg-yellow-500','bg-purple-500','bg-pink-500','bg-indigo-500','bg-zinc-500','bg-natural-500','bg-stone-500','bg-violet-500','bg-cyan-500','bg-emerald-500']
  let taskColor: number[] = []
  let date = startDate
  let user = 0

  const renderHours = () => {
    const hours = [];
    for (let hour = 0; hour <= hoursBetween; hour++) {
      const formattedHour = (startDate.getHours() + hour) % 24;
      hours.push(formattedHour)
    }
    return hours;
  };
  
  const hours = renderHours();
  
  function getColors(index: number) {
    if (index != user) {
      date = startDate
      user = index
    }
    taskColor = []
    const top = new Date(date.getFullYear(), date.getMonth(), date.getDate(), date.getHours() + 1)
    users[index].taskRange.map(range => {
        if (isCollitionDateRanges({
          start_time: date,
          end_time: top,
        }, range)) taskColor.push(users[index].taskRange.indexOf(range))
      })

    date = top
    return taskColor.length
  }


  return (
    <div className="overflow-x-auto">
      <table className="min-w-full bg-white shadow-md rounded-lg overflow-hidden">
        <thead className="bg-gray-50">
          <tr>
            <th className="px-4 py-2 text-left">Hour</th>
            {hours.map(hour => (
              <th key={hour} className="px-4 py-2 text-center">{hour}:00</th>
            ))}
          </tr>
        </thead>
        <tbody>
          {users.map((_, key) => (
            <tr key={key}>
              <td className="border px-4 py-2 text-center"></td>
              {hours.map(hour => (
                <td key={hour} className={`border text-center grid-fils-${getColors(key)}`}>
                  {taskColor.map(i => (
                    <div className={`${colors[i]} h-4`}></div>
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