import { useState, useEffect } from "react";

import { Task } from "../../types/task";
import SelectStatus from "./Select/SelectStatus";
import DatePickerOne from "./DatePicker/DatePickerOne";
import SelectType from "./Select/SelectEventType";
import { Group } from "../../types/group";
import api from "../../api/axios";
import Warning from "../Alerts/Warning";

type props = {
  header: string;
  edit: any;
  old_task: Task | undefined;
  set: React.Dispatch<React.SetStateAction<boolean>>;
}

const TaskForm = ({header, edit, old_task, set}: props) => {
  const [ title, setTitle ] = useState<string>(old_task ? old_task.title : '')
  const [ description, setDescription ] = useState<string>(old_task ? old_task.description : '')
  const [ status, setStatus ] = useState<string>(old_task ? old_task.status : '')
  const [ startTime, setStartTime ] = useState<Date>(old_task ? new Date(old_task.start_time) : new Date())
  const [ endTime, setEndTime ] = useState<Date>(old_task ? new Date(old_task.end_time) : new Date())
  const [ eventType, setEventType ] = useState<string>(old_task ? old_task.event_type : '')
  const [ group, setGroup ] = useState<string | null>(old_task ? old_task.group : '')
  const [ groups, setGroups ] = useState<Group[]>([]);
  const [ warning, setWarning ] = useState<boolean | undefined>(false);

  useEffect(() => {
    const fetchGroups = async () => {
      try {
        const response = await api.get('/groups/all');
        setGroups(response.data);
      } catch (error) {
        console.error('Error al obtener grupos:', error);
      }
    };

    fetchGroups();
  }, []);

  useEffect(() => {
    if (eventType != 'group') setGroup('')
  },[eventType])

  useEffect(() => {
    const g = groups.find(g => g.name === group);
    setWarning(g && !g.is_my);
    setStatus("pending");
  }, [group]);

  function create() {
    const task = {
      id: old_task ? old_task.id : null,
      title: title,
      description: description,
      status: status,
      start_time: startTime,
      end_time: endTime,
      event_type: eventType,
      group_name: group, 
      by_owner: !warning
    }

    edit(task);
  }

  return (
      <div className="gap-9">
      <div className="flex flex-col gap-9">
        {/* <!-- Contact Form --> */}
        <div className="rounded-sm border border-stroke bg-white shadow-default dark:border-strokedark dark:bg-boxdark">
          <div className="border-b border-stroke py-4 px-6.5 dark:border-strokedark">
            <h3 className="font-medium text-black dark:text-white">
              {header}
            </h3>
          </div>
          <form action="#">
            <div className="p-6.5">
              <div className="mb-4.5 flex flex-col gap-6 xl:flex-row">
                <div className="w-full xl:w-1/2">
                  <label className="mb-2.5 block text-black dark:text-white">
                    Title
                  </label>
                  <input
                    type="text"
                    placeholder="Title"
                    value={title}
                    onChange={(e) => setTitle(e.target.value)}
                    className="w-full rounded border-[1.5px] border-stroke bg-transparent py-3 px-5 text-black outline-none transition focus:border-primary active:border-primary disabled:cursor-default disabled:bg-whiter dark:border-form-strokedark dark:bg-form-input dark:text-white dark:focus:border-primary"
                  />
                </div>
              </div>
              <div className="mb-6">
                <label className="mb-2.5 block text-black dark:text-white">
                  Description
                </label>
                <textarea
                  rows={4}
                  placeholder="Description"
                  value={description}
                  onChange={(e) => setDescription(e.target.value)}
                  className="w-full rounded border-[1.5px] border-stroke bg-transparent py-3 px-5 text-black outline-none transition focus:border-primary active:border-primary disabled:cursor-default disabled:bg-whiter dark:border-form-strokedark dark:bg-form-input dark:text-white dark:focus:border-primary"
                ></textarea>
              </div>

              { !warning && (
                <div className="mb-6">
                  <label className="mb-2.5 block text-black dark:text-white">
                    Status
                  </label>
                  <SelectStatus value={status} set={setStatus}/>
                </div>
              )}
              
              <div className="mb-6">
                <label className="mb-2.5 block text-black dark:text-white">
                  Start Time
                </label>
                <DatePickerOne date={new Date(startTime.getFullYear(), startTime.getMonth(), startTime.getDate(), startTime.getHours() - 5, startTime.getMinutes()).toISOString().slice(0,16)} set={setStartTime}/>
              </div>
              <div className="mb-6">
                <label className="mb-2.5 block text-black dark:text-white">
                  End Time
                </label>
                <DatePickerOne date={new Date(endTime.getFullYear(), endTime.getMonth(), endTime.getDate(), endTime.getHours() - 5, endTime.getMinutes()).toISOString().slice(0,16)} set={setEndTime}/>
              </div>
              <div className="mb-6">
                <label className="mb-2.5 block text-black dark:text-white">
                  Type
                </label>
                <SelectType value={eventType} set={setEventType}/>
              </div>
              { (eventType == 'group' || eventType == 'hierarchical') && (
                <div className="mb-6">
                  <label className="mb-2.5 block text-black dark:text-white">
                    Group
                  </label>
                  
                  { warning && (
                    <Warning 
                      msg="Please be advised that a new task will be created shortly. Once the task is created, you will have the opportunity to review it and either accept or decline based on your availability and workload."
                    />
                  )}

                  <select
                    value={group || ''}
                    onChange={(e) => setGroup(e.target.value || null)}
                    className="w-full rounded border-[1.5px] border-stroke bg-transparent py-3 px-5 text-black outline-none transition focus:border-primary dark:border-form-strokedark dark:bg-form-input dark:text-white"
                  >
                    <option value="">None</option>
                    {groups.map(g => (
                      <option key={g.id} value={g.name}>{g.is_my ? '👑' : '🔹'} {g.name}</option>
                    ))}
                  </select>
                </div>
              )}
              
              <div className="grid grid-cols-2 w-full justify-center rounded p-3">
                <button onClick={() => create()} className="flex justify-center rounded bg-primary p-3 font-medium text-gray hover:bg-opacity-90 m-5">
                  {header}
                </button>
                <button onClick={() => set(false)} className="flex justify-center rounded bg-primary p-3 font-medium text-gray hover:bg-opacity-90 m-5">
                  Cancel
                </button>
              </div>
            </div>
          </form>
        </div>
      </div>
    </div>
  )
}

export default TaskForm;