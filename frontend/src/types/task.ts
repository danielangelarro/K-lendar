
export type TaskCreate = {
  title: string;
  description: string;
  group: string;
  status: string;
  start_time: Date;
  end_time: Date;
  event_type: string;
};
  
export type Task = {
    id: number;
    title: string;
    description: string;
    group: string;
    status: string;
    start_time: Date;
    end_time: Date;
    event_type: string;
  };