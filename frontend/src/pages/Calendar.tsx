import { useEffect, useState } from "react";

export type Range = {
    start_time: Date;
    end_time: Date;
}

const timeData: Range[] = [
    {
      start_time: new Date(2024,10,7),
      end_time: new Date(2024,11,7),
    },
    {
      start_time: new Date(2024,10,27),
      end_time: new Date(2024,11,4),
    },
    {
      start_time: new Date(2024,10,6),
      end_time: new Date(2024,11,6),
    },
    {
      start_time: new Date(2024,10,9),
      end_time: new Date(2024,11,11),
    },
  ];

  export function isCollitionDateRanges(range1: Range, range2: Range): boolean {
    if (range1.end_time < range2.start_time || range1.start_time >= range2.end_time ) return false;
    return true;
  }

export default function component() {
    const monthNames = ['January', 'February', 'March', 'April', 'May', 'June', 'July', 'August', 'September', 'October', 'November', 'December'];
    const daysOfWeek = ['Sun', 'Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat'];
    const [ selectedDate, setSelectedDate ] = useState<Date>(new Date());
    const [ month, setMonth ] = useState<number>(selectedDate.getMonth())
    const [ year, setYear ] = useState<number>(selectedDate.getFullYear())
    const [ modal, setModal ] = useState<boolean>(false)

    useEffect(() => {
        generateCalendar()
        const dayElements = document.querySelectorAll('.cursor-pointer');
        dayElements.forEach(dayElement => {
            dayElement.addEventListener('click', () => {
                const day = parseInt(dayElement.id);
                setSelectedDate(new Date(year, month, day));
                setModal(true)
            });
        });
    },[month])

    // const filteredEvents = taskData.filter(event => 
    //   isDateInRange(event.start_time, new Date(year, month, 1), new Date(year, month + 1, 0))
    // );

    function generateCalendar() {
        const calendarElement = document.getElementById('calendar');
        const currentMonthElement = document.getElementById('currentMonth');
        
        const firstDayOfMonth = new Date(year, month, 1);
        const daysInMonth = new Date(year, month + 1, 0).getDate();
        
        if (calendarElement && currentMonthElement) {
            calendarElement.innerHTML = '';
                
            const firstDayOfWeek = firstDayOfMonth.getDay();
        
            for (let i = 0; i < firstDayOfWeek; i++) {
                const emptyDayElement = document.createElement('div');
                calendarElement.appendChild(emptyDayElement);
            }
        
            for (let day = 1; day <= daysInMonth; day++) {
                const dayElement = document.createElement('div');
                dayElement.className = 'text-center py-2 border cursor-pointer';
                dayElement.id = `${day}`
                dayElement.innerText = `${day}`;

                timeData.map(range => {
                    if (isCollitionDateRanges({
                        start_time: new Date(year,month,day),
                        end_time: new Date(year,month,day,23,59,59),
                    }, range)) {
                        dayElement.classList.add('bg-blue-500', 'text-white');
                    }
                })
                
                calendarElement.appendChild(dayElement);
            }
        }
    }
    
    function previous() {
        setMonth(month - 1);
        if (month < 0) {
            setMonth(11);
            setYear(year - 1);
        }
    }
    
    function next() {
        setMonth(month + 1);
        if (month > 11) {
            setMonth(0);
            setYear(year + 1);
        }
    }
    
    return (
        <div className="bg-gray-100 flex items-center justify-center h-screen">
            <div className="lg:w-7/12 md:w-9/12 sm:w-10/12 mx-auto p-4">
                <div className="bg-white shadow-lg rounded-lg overflow-hidden">
                    <div className="flex items-center justify-between px-6 py-3 bg-gray-700">
                        <button id="prevMonth" onClick={() => previous()} className="text-white">Previous</button>
                        <h2 id="currentMonth" className="text-white">
                            {`${monthNames[month]} ${year}`}
                        </h2>
                        <button id="nextMonth" onClick={() => next()} className="text-white">Next</button>
                    </div>
                    <div className="grid grid-cols-7 gap-2 p-4" id="days">
                        {daysOfWeek.map((day) => (
                            <div className="text-center font-semibold">
                                {day}
                            </div>
                        ))}
                    </div>
                    <div className="grid grid-cols-7 gap-2 p-4" id="calendar">
                        {/* <!-- Calendar Days Go Here --> */} 
                    </div>
                    {modal && (
                        <div id="myModal" className="modal fixed inset-0 flex items-center justify-center z-50">
                            <div className="modal-overlay absolute inset-0 bg-black opacity-50"></div>
                            
                            <div className="modal-container bg-white w-11/12 md:max-w-md mx-auto rounded shadow-lg z-50 overflow-y-auto">
                                <div className="modal-content py-4 text-left px-6">
                                <div className="flex justify-between items-center pb-3">
                                    <p className="text-2xl font-bold">Selected Date</p>
                                    <button id="closeModal" onClick={() => setModal(false)} className="modal-close px-3 py-1 rounded-full bg-gray-200 hover:bg-gray-300 focus:outline-none focus:ring">✕</button>
                                </div>
                                <div id="modalDate" className="text-xl font-semibold">
                                    {selectedDate.toDateString()}
                                </div>
                                </div>
                            </div>
                        </div>
                    )}
                </div>
            </div>
        </div>
    )
}