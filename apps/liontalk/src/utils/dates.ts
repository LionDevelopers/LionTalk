import { Seminar } from '../types';

const MONTH_MAP: { [key: string]: number } = {
  jan: 0, january: 0,
  feb: 1, february: 1,
  mar: 2, march: 2,
  apr: 3, april: 3,
  may: 4,
  jun: 5, june: 5,
  jul: 6, july: 6,
  aug: 7, august: 7,
  sep: 8, sept: 8, september: 8,
  oct: 9, october: 9,
  nov: 10, november: 10,
  dec: 11, december: 11
};

export const parseSeminarDate = (dateStr: string, timeStr: string) => {
  try {
    // Parse Date: "8-Sept-25" or "8-September-2025" -> [8, 8, 2025]
    const [dayStr, monthStr, yearStr] = dateStr.split('-');
    const day = parseInt(dayStr, 10);
    const month = MONTH_MAP[monthStr?.toLowerCase()];
    const yearNum = parseInt(yearStr, 10);

    if (isNaN(day) || month === undefined || isNaN(yearNum)) {
      return { startDate: null, endDate: null, monthAbbr: monthStr ?? '', dayDisplay: dayStr ?? '' };
    }

    const year = yearNum >= 1000 ? yearNum : 2000 + yearNum;

    // Parse Time: "4:10 pm - 5:00 pm", "12:00 - 1:00 pm", or "4:30p-6:00p"
    const [startTimeStr, endTimeStr] = timeStr.split('-').map(s => s.trim());

    const parseTime = (tStr: string, isEnd: boolean = false) => {
      if (!tStr) return { hours: 0, minutes: 0, meridiem: undefined as string | undefined };

      // Meridiem may be spelled out ("am"/"pm") or abbreviated to a single letter ("a"/"p")
      const match = tStr.match(/(\d+):(\d+)\s*(am|pm|a|p)?/i);
      if (!match) return { hours: 0, minutes: 0, meridiem: undefined };

      const [, h, m, rawMeridiem] = match;
      let hours = parseInt(h, 10);
      const minutes = parseInt(m, 10);
      let meridiem = rawMeridiem?.toLowerCase();

      // Handle missing meridiem (e.g. "12:00 - 1:00 pm", assume first is same as second if missing)
      if (!meridiem && isEnd) meridiem = 'pm'; // Fallback

      // Convert to 24h
      if (meridiem?.startsWith('p') && hours < 12) hours += 12;
      if (meridiem?.startsWith('a') && hours === 12) hours = 0;

      return { hours, minutes, meridiem };
    };

    const start = parseTime(startTimeStr);
    const end = parseTime(endTimeStr, true);
    // If start has no explicit meridiem, inherit the end's (usually PM for seminars)
    if (!start.meridiem && end.meridiem?.startsWith('p') && start.hours < 12) {
        start.hours += 12;
    }

    const startDate = new Date(year, month, day, start.hours, start.minutes);
    let endDate = new Date(year, month, day, end.hours, end.minutes);
    
    // Fallback duration
    if (endDate <= startDate) {
      endDate = new Date(startDate.getTime() + 60 * 60 * 1000); 
    }

    return { startDate: startDate as Date | null, endDate: endDate as Date | null, monthAbbr: monthStr.slice(0, 3), dayDisplay: dayStr };
  } catch (e) {
    console.error("Date parse error", e);
    return { startDate: null, endDate: null, monthAbbr: 'ERR', dayDisplay: '00' };
  }
};

export const getGoogleCalendarLink = (seminar: Seminar) => {
  const { startDate, endDate } = parseSeminarDate(seminar.date, seminar.time);
  if (!startDate || !endDate) return null;
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