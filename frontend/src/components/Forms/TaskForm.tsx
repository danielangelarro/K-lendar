import { useState, useEffect } from "react";

import { Task } from "../../types/task";
import SelectStatus from "./SelectGroup/SelectStatus";
import DatePickerOne from "./DatePicker/DatePickerOne";
import SelectType from "./SelectGroup/SelectEventType";

type props = {
  header: string;
  edit: any;
  old_task: Task | undefined;
}

const TaskForm = ({header, edit, old_task}: props) => {
  const [ title, setTitle ] = useState<string>(old_task ? old_task.title : '')
  const [ description, setDescription ] = useState<string>(old_task ? old_task.description : '')
  const [ status, setStatus ] = useState<string>(old_task ? old_task.status : '')
  const [ startTime, setStartTime ] = useState<Date>(old_task ? old_task.start_time : new Date())
  const [ endTime, setEndTime ] = useState<Date>(old_task ? old_task.end_time : new Date())
  const [ eventType, setEventType ] = useState<string>(old_task ? old_task.event_type : '')
  const [ group, setGroup ] = useState<string>(old_task ? old_task.group : '')

  useEffect(() => {
    if (eventType != 'group') setGroup('')
  },[eventType])

  function create() {
    const task = {
      id: old_task ? old_task.id : -1,
      title: title,
      description: description,
      status: status,
      start_time: startTime,
      end_time: endTime,
      event_type: eventType,
      group: group, 
    }

    edit(task)
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
              <div className="mb-6">
                <label className="mb-2.5 block text-black dark:text-white">
                  Status
                </label>
                <SelectStatus value={status} set={setStatus}/>
              </div>
              
              <div className="mb-6">
                <label className="mb-2.5 block text-black dark:text-white">
                  Start Time
                </label>
                <DatePickerOne date={startTime.toDateString()} set={setStartTime}/>
              </div>
              <div className="mb-6">
                <label className="mb-2.5 block text-black dark:text-white">
                  End Time
                </label>
                <DatePickerOne date={endTime.toDateString()} set={setEndTime}/>
              </div>
              <div className="mb-6">
                <label className="mb-2.5 block text-black dark:text-white">
                  Type
                </label>
                <SelectType value={eventType} set={setEventType}/>
              </div>
              { eventType == 'group' && (
                <div className="mb-6">
                  <label className="mb-2.5 block text-black dark:text-white">
                    Group
                  </label>
                  <input
                    type="text"
                    placeholder="Group"
                    value={group}
                    onChange={(e) => setGroup(e.target.value)}
                    className="w-full rounded border-[1.5px] border-stroke bg-transparent py-3 px-5 text-black outline-none transition focus:border-primary active:border-primary disabled:cursor-default disabled:bg-whiter dark:border-form-strokedark dark:bg-form-input dark:text-white dark:focus:border-primary"
                  />
                </div>
              )}
              
              <button onClick={() => create()} className="flex w-full justify-center rounded bg-primary p-3 font-medium text-gray hover:bg-opacity-90">
                {header}
              </button>
            </div>
          </form>
        </div>
      </div>
    </div>
  )
}

export default TaskForm;