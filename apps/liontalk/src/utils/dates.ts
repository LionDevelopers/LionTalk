import { Seminar } from '../types';

const MONTH_MAP: { [key: string]: number } = {
  Jan: 0, Feb: 1, Mar: 2, Apr: 3, May: 4, Jun: 5,
  Jul: 6, Aug: 7, Sep: 8, Sept: 8, Oct: 9, Nov: 10, Dec: 11
};

export const parseSeminarDate = (dateStr: string, timeStr: string) => {
  try {
    // Parse Date: "8-Sept-25" -> [8, 8, 2025]
    const [dayStr, monthStr, yearStr] = dateStr.split('-');
    const day = parseInt(dayStr, 10);
    const month = MONTH_MAP[monthStr] ?? 0;
    const year = 2000 + parseInt(yearStr, 10);

    // Parse Time: "4:10 pm - 5:00 pm" or "12:00 - 1:00 pm"
    const [startTimeStr, endTimeStr] = timeStr.split('-').map(s => s.trim());
    
    const parseTime = (tStr: string, isEnd: boolean = false) => {
      if (!tStr) return { hours: 0, minutes: 0 };
      
      const match = tStr.match(/(\d+):(\d+)\s*(am|pm)?/i);
      if (!match) return { hours: 0, minutes: 0 };

      let [_, h, m, meridiem] = match;
      let hours = parseInt(h, 10);
      const minutes = parseInt(m, 10);

      // Handle missing meridiem (e.g. "12:00 - 1:00 pm", assume first is same as second if missing)
      if (!meridiem && isEnd) meridiem = 'pm'; // Fallback
      
      // Convert to 24h
      const isPm = meridiem?.toLowerCase() === 'pm';
      const isAm = meridiem?.toLowerCase() === 'am';
      
      if (isPm && hours < 12) hours += 12;
      if (isAm && hours === 12) hours = 0;
      
      return { hours, minutes };
    };

    const start = parseTime(startTimeStr);
    // If start has no meridiem, inherit from end (logic omitted for brevity, usually safe to assume PM for seminars)
    if (startTimeStr.indexOf('m') === -1 && timeStr.includes('pm') && start.hours < 12) {
        start.hours += 12;
    }

    const end = parseTime(endTimeStr, true);

    const startDate = new Date(year, month, day, start.hours, start.minutes);
    let endDate = new Date(year, month, day, end.hours, end.minutes);
    
    // Fallback duration
    if (endDate <= startDate) {
      endDate = new Date(startDate.getTime() + 60 * 60 * 1000); 
    }

    return { startDate, endDate, monthAbbr: monthStr, dayDisplay: dayStr };
  } catch (e) {
    console.error("Date parse error", e);
    return { startDate: new Date(), endDate: new Date(), monthAbbr: 'ERR', dayDisplay: '00' };
  }
};

export const getGoogleCalendarLink = (seminar: Seminar) => {
  const { startDate, endDate } = parseSeminarDate(seminar.date, seminar.time);
  const fmt = (d: Date) => d.toISOString().replace(/-|:|\.\d\d\d/g, "");

  const params = new URLSearchParams({
    action: "TEMPLATE",
    text: `LionTalk: ${seminar.seminar_title}`,
    dates: `${fmt(startDate)}/${fmt(endDate)}`,
    details: `Department: ${seminar.department}\nSeries: ${seminar.series || 'N/A'}\nSpeaker: ${seminar.speaker}\nAffiliation: ${seminar.affiliation}\n\nAbstract: ${seminar.abstract}`,
    location: seminar.location,
  });

  return `https://calendar.google.com/calendar/render?${params.toString()}`;
};