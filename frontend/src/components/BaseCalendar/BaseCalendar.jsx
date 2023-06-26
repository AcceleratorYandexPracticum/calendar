/* Core */
import { React, useCallback, useContext } from 'react';
import PropTypes from 'prop-types';

/* Libraries */
import { Calendar } from 'react-big-calendar';

/* Instruments */
import { culture, messages, noop } from '../../utils/constants';
import { CalendarsContext, LocalizationContext } from '../../context';
import styles from './BaseCalendar.module.css';

export function BaseCalendar({ onEventDoubleClick, onNewEventClick }) {
	const localizer = useContext(LocalizationContext);
	const { format } = localizer;

	const { holidays, allUserEvents, chosenCalendars, setEditableEvent } =
		useContext(CalendarsContext);

	// TODO: потом сюда добавятся события пошаренных календарей
	const displayedEvents = [...holidays, ...allUserEvents].filter((e) =>
		chosenCalendars.includes(e.calendar.id)
	);

	const { defaultDate, formats } = {
		defaultDate: new Date(),
		formats: {
			weekdayFormat: (date) => format(date, 'eeee', culture),
			monthHeaderFormat: (date) => format(date, 'LLLL yyyy', culture),
		},
	};

	// окрашивание событий
	const eventPropGetter = useCallback(
		(event) => ({ style: { backgroundColor: event.calendar.color } }),
		[]
	);

	const handleDoubleClick = (event) => {
		if (event.calendar.id === 1) {
			return;
		}
		onEventDoubleClick(true);
		setEditableEvent(event);
	};

	const handleSelectSlot = () => onNewEventClick(true);

	return (
		<Calendar
			dayPropGetter={(date) => {
				const dayOfWeek = date.getDay();
				const dateOfMonth = date.getMonth();
				const nowMonth = new Date().getMonth();
				const nowDay = new Date().getDate();
				const dayOfMonth = date.getDate();

				if (dateOfMonth !== nowMonth) {
					return { className: styles.otherMonth };
				}
				if (nowDay === dayOfMonth && nowMonth === dateOfMonth) {
					return { className: styles.today };
				}
				return dayOfWeek === 0 || dayOfWeek === 6
					? { className: styles.holiday }
					: {};
			}}
			defaultDate={defaultDate}
			localizer={localizer}
			startAccessor="start"
			endAccessor="end"
			culture={culture}
			formats={formats}
			events={displayedEvents}
			className={styles.calendar}
			messages={messages}
			eventPropGetter={eventPropGetter}
			onDoubleClickEvent={handleDoubleClick}
			onSelectSlot={handleSelectSlot}
			selectable
		/>
	);
}

BaseCalendar.propTypes = {
	onEventDoubleClick: PropTypes.func,
	onNewEventClick: PropTypes.func,
};

BaseCalendar.defaultProps = {
	onEventDoubleClick: noop,
	onNewEventClick: noop,
};
