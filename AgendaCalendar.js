import React, { useState, useEffect } from 'react';
import { format, addDays, parseISO } from 'date-fns';

const colors = [
  '#FF6B6B', '#4ECDC4', '#45B7D1', '#FFA07A', '#98D8C8',
  '#F06292', '#AED581', '#7986CB', '#FFD54F', '#A1887F'
];

const AssignmentItem = ({ assignment, color }) => (
  <div className="flex items-center mb-1">
    <div className={`w-3 h-3 rounded-full mr-2`} style={{ backgroundColor: color }}></div>
    <span className="text-sm">{assignment.SUMMARY} ({assignment.COURSE})</span>
  </div>
);

const DayCard = ({ date, assignments, courseColors }) => (
  <div className="bg-white rounded-lg shadow-md p-4 mb-4">
    <h3 className="text-lg font-semibold mb-2">
      {format(date, 'EEEE, MMMM d, yyyy')}
    </h3>
    {assignments.map((assignment, index) => (
      <AssignmentItem 
        key={index} 
        assignment={assignment} 
        color={courseColors[assignment.COURSE]}
      />
    ))}
  </div>
);

const AgendaCalendar = ({ assignments }) => {
  const [days, setDays] = useState([]);
  const [courseColors, setCourseColors] = useState({});

  useEffect(() => {
    const today = new Date();
    const nextSixtyDays = Array.from({ length: 60 }, (_, i) => addDays(today, i));
    setDays(nextSixtyDays);

    const courses = [...new Set(assignments.map(a => a.COURSE))].sort();
    const colorMap = Object.fromEntries(
      courses.map((course, index) => [course, colors[index % colors.length]])
    );
    setCourseColors(colorMap);
  }, [assignments]);

  const getAssignmentsForDate = (date) => {
    return assignments.filter(a => {
      const assignmentDate = parseISO(a.DTSTART.split('T')[0]);
      return format(assignmentDate, 'yyyy-MM-dd') === format(date, 'yyyy-MM-dd');
    });
  };

  return (
    <div className="p-4">
      <h2 className="text-2xl font-bold mb-4">60-Day Agenda</h2>
      {days.map((day, index) => (
        <DayCard 
          key={index}
          date={day}
          assignments={getAssignmentsForDate(day)}
          courseColors={courseColors}
        />
      ))}
    </div>
  );
};

export default AgendaCalendar;