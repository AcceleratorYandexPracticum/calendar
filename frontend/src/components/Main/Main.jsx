import React, { useState } from 'react';
import PropTypes from 'prop-types';
import { Sidebar } from '../Sidebar/Sidebar';
import { BaseCalendar } from '../BaseCalendar/BaseCalendar';
import styles from './Main.module.css';
import { YearCalendar } from '../YearCalendar/YearCalendar';

export function Main({
	localizer,
	onNewEventClick,
	onNewCalendarClick,
	events,
  allUserCalendars,
}) {
	const [visibleProdCalendar, setVisibleProdCalendar] = useState(false);

	return (
		<main className={`${styles.main} container`}>
			<Sidebar
				onNewEventClick={onNewEventClick}
				onNewCalendarClick={onNewCalendarClick}
				localizer={localizer}
				showProdCalendar={setVisibleProdCalendar}
				visibleProdCalendar={visibleProdCalendar}
        allUserCalendars={allUserCalendars}
			/>
			<div className={styles.content}>
				<BaseCalendar localizer={localizer} events={events} />
				{visibleProdCalendar && <YearCalendar localizer={localizer} />}
			</div>
		</main>
	);
}

Main.propTypes = {
	// eslint-disable-next-line react/forbid-prop-types
	localizer: PropTypes.object.isRequired,
	onNewEventClick: PropTypes.func.isRequired,
	onNewCalendarClick: PropTypes.func.isRequired,
	// eslint-disable-next-line react/forbid-prop-types
	events: PropTypes.array.isRequired,
  // eslint-disable-next-line react/forbid-prop-types
  allUserCalendars: PropTypes.array.isRequired,
};
