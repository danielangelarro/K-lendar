'use client'

import { useState, useEffect } from 'react'
import { Calendar } from "@/components/ui/calendar"
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs"
import { Card, CardContent, CardDescription, CardFooter, CardHeader, CardTitle } from "@/components/ui/card"

import { Input } from "@/components/ui/input"
import { Button } from "@/components/ui/button"
import { Label } from "@/components/ui/label"
import { Checkbox } from "@/components/ui/checkbox"
import { Dialog, DialogContent, DialogDescription, DialogFooter, DialogHeader, DialogTitle, DialogTrigger } from "@/components/ui/dialog"
import { format, isSameDay } from 'date-fns'

type Tarea = {
  id: number;
  texto: string;
  completada: boolean;
  fecha: Date;
}

export default function Component() {
  const [date, setDate] = useState<Date | undefined>()
  const [tareas, setTareas] = useState<Tarea[]>([])
  const [nuevaTarea, setNuevaTarea] = useState("")
  const [nuevaFecha, setNuevaFecha] = useState<Date | undefined>(new Date())
  const [modalAbierto, setModalAbierto] = useState(false)
  const [diasConTareas, setDiasConTareas] = useState<Date[]>([])
  const [tareasFiltradas, setTareasFiltradas] = useState<Tarea[]>([])
  const [tabActiva, setTabActiva] = useState("calendario")

  useEffect(() => {
    actualizarDiasConTareas()
  }, [tareas])

  useEffect(() => {
    if (date) {
      const tareasDeDia = tareas.filter(tarea => isSameDay(tarea.fecha, date))
      setTareasFiltradas(tareasDeDia)
    }
  }, [date, tareas])

  const actualizarDiasConTareas = () => {
    const dias = tareas
      .filter(tarea => !tarea.completada)
      .map(tarea => new Date(tarea.fecha.getFullYear(), tarea.fecha.getMonth(), tarea.fecha.getDate()))
    setDiasConTareas(dias)
  }

  const agregarTarea = () => {
    if (nuevaTarea.trim() !== "" && nuevaFecha) {
      setTareas([...tareas, { 
        id: Date.now(), 
        texto: nuevaTarea, 
        completada: false,
        fecha: nuevaFecha
      }])
      setNuevaTarea("")
      setNuevaFecha(new Date())
      setModalAbierto(false)
    }
  }

  const toggleTarea = (id: number) => {
    setTareas(tareas.map(tarea => 
      tarea.id === id ? { ...tarea, completada: !tarea.completada } : tarea
    ))
  }

  const handleDateSelect = (selectedDate: Date | undefined) => {
    setDate(selectedDate)
    if (selectedDate) {
      setTabActiva("tareas")
    }
  }

  return (
    <Card className="w-full max-w-3xl mx-auto">
      <CardHeader>
        <CardTitle>Calendario y Tareas</CardTitle>
        <CardDescription>Gestiona tu tiempo y tus tareas</CardDescription>
      </CardHeader>
      <CardContent>
        <Tabs value={tabActiva} onValueChange={setTabActiva} className="w-full">
          <TabsList className="grid w-full grid-cols-2">
            <TabsTrigger value="calendario">Calendario</TabsTrigger>
            <TabsTrigger value="tareas">Lista de Tareas</TabsTrigger>
          </TabsList>
          <TabsContent value="calendario">
            <Calendar
              mode="single"
              selected={date}
              onSelect={handleDateSelect}
              className="rounded-md border"
              modifiers={{highlight: diasConTareas}}
              modifiersStyles={{
                highlight: { backgroundColor: 'blue', color: 'white' } 
              }}
            />
          </TabsContent>
          <TabsContent value="tareas">
            <div className="space-y-4">
              <div className="space-y-2">
                {(date ? tareasFiltradas : tareas).map(tarea => (
                  <div key={tarea.id} className="flex items-center space-x-2">
                    <Checkbox 
                      id={`tarea-${tarea.id}`} 
                      checked={tarea.completada}
                      onCheckedChange={() => toggleTarea(tarea.id)}
                    />
                    <Label 
                      htmlFor={`tarea-${tarea.id}`}
                      className={tarea.completada ? "line-through" : ""}
                    >
                      {tarea.texto} - {format(tarea.fecha, 'dd/MM/yyyy HH:mm')}
                    </Label>
                  </div>
                ))}
              </div>
              <Dialog open={modalAbierto} onOpenChange={setModalAbierto}>
                <DialogTrigger asChild>
                  <Button>Agregar Tarea</Button>
                </DialogTrigger>
                <DialogContent className="sm:max-w-[425px]">
                  <DialogHeader>
                    <DialogTitle>Agregar Nueva Tarea</DialogTitle>
                    <DialogDescription>
                      Ingresa los detalles de la nueva tarea aquí.
                    </DialogDescription>
                  </DialogHeader>
                  <div className="grid gap-4 py-4">
                    <div className="grid grid-cols-4 items-center gap-4">
                      <Label htmlFor="tarea" className="text-right">
                        Tarea
                      </Label>
                      <Input
                        id="tarea"
                        value={nuevaTarea}
                        onChange={(e) => setNuevaTarea(e.target.value)}
                        className="col-span-3"
                      />
                    </div>
                    <div className="grid grid-cols-4 items-center gap-4">
                      <Label htmlFor="fecha" className="text-right">
                        Fecha y Hora
                      </Label>
                      <Input
                        id="fecha"
                        type="datetime-local"
                        value={nuevaFecha ? format(nuevaFecha, "yyyy-MM-dd'T'HH:mm") : ''}
                        onChange={(e) => setNuevaFecha(new Date(e.target.value))}
                        className="col-span-3"
                      />
                    </div>
                  </div>
                  <DialogFooter>
                    <Button onClick={agregarTarea}>Agregar Tarea</Button>
                  </DialogFooter>
                </DialogContent>
              </Dialog>
            </div>
          </TabsContent>
        </Tabs>
      </CardContent>
      <CardFooter>
        <p className="text-sm text-muted-foreground">
          {date 
            ? `Tienes ${tareasFiltradas.filter(t => !t.completada).length} tareas pendientes para el ${format(date, 'dd/MM/yyyy')}.`
            : `Tienes ${tareas.filter(t => !t.completada).length} tareas pendientes en total.`
          }
        </p>
      </CardFooter>
    </Card>
  )
}
