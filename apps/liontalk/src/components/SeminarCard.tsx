import React from 'react';
import { Seminar } from '../types'; // Adjust path if needed (e.g. '../index')

export const SeminarCard = ({ seminar }: { seminar: Seminar }) => {
  const isHoliday = seminar.speaker === "N/A";

  return (
    <div
      className={`rounded-lg shadow-md overflow-hidden border ${
        isHoliday
          ? 'bg-gray-100 border-gray-200 opacity-75'
          : 'bg-white border-gray-200'
      }`}
    >
      <div className="p-6">
        {/* Header: Date and Time */}
        <div className="flex flex-col sm:flex-row sm:justify-between sm:items-center mb-4">
          <div className="flex items-center space-x-2 text-indigo-600 font-semibold">
            <span>{seminar.date}</span>
            <span>•</span>
            <span>{seminar.time}</span>
          </div>
          <div className="text-sm text-gray-500 mt-1 sm:mt-0">
            {seminar.location}
          </div>
        </div>

        {/* Title */}
        <h2
          className={`text-2xl font-bold mb-2 ${
            isHoliday ? 'text-gray-500 italic' : 'text-gray-900'
          }`}
        >
          {seminar.seminar_title}
        </h2>

        {/* Speaker Info */}
        {!isHoliday && (
          <>
            <div className="mb-4">
              <span className="text-lg font-medium text-gray-800">
                {seminar.speaker}
              </span>
              {seminar.affiliation && (
                <span className="text-gray-600 ml-2">
                  ({seminar.affiliation})
                </span>
              )}
            </div>

            {/* Details: Abstract & Bio */}
            <div className="space-y-4 text-gray-700">
              <details className="group">
                <summary className="cursor-pointer font-medium text-indigo-600 hover:text-indigo-800 focus:outline-none">
                  Read Abstract
                </summary>
                <p className="mt-2 text-sm leading-relaxed border-l-4 border-indigo-100 pl-4">
                  {seminar.abstract}
                </p>
              </details>

              {seminar.bio && (
                <details className="group">
                  <summary className="cursor-pointer font-medium text-indigo-600 hover:text-indigo-800 focus:outline-none">
                    Speaker Bio
                  </summary>
                  <p className="mt-2 text-sm leading-relaxed border-l-4 border-indigo-100 pl-4 italic">
                    {seminar.bio}
                  </p>
                </details>
              )}
            </div>
          </>
        )}
      </div>
    </div>
  );
};