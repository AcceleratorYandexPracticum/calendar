import React, { useState } from 'react';
import PropTypes from 'prop-types';
import { Dialog } from 'primereact/dialog';
import { FormLogin } from '../FormLogin/FormLogin';
import { FormRegistration } from '../FormRegistration/FormRegistration';

export function PopupLogin({
	visible,
	setVisible,
	handleRegister,
	handleLogin,
  setShowMessage,
	message,
	isError,
}) {
	const [showFormLogin, setShowFormLogin] = useState(true);

	const handleOverlayClick = (evt) => {
		if (evt.target === evt.currentTarget) {
			setVisible(false);
		}
	};

	return (
		<Dialog
			visible={visible}
			onHide={() => setVisible(false)}
			onMaskClick={handleOverlayClick}
			blockScroll
		>
			{showFormLogin ? (
				<FormLogin
					showFormLogin={setShowFormLogin}
					handleLogin={handleLogin}
					message={message}
					isError={isError}
          setShowMessage={setShowMessage}
				/>
			) : (
				<FormRegistration
					showFormLogin={setShowFormLogin}
					handleRegister={handleRegister}
					message={message}
					isError={isError}
          setShowMessage={setShowMessage}
				/>
			)}
		</Dialog>
	);
}

PopupLogin.propTypes = {
	visible: PropTypes.bool.isRequired,
	setVisible: PropTypes.func.isRequired,
	handleRegister: PropTypes.func.isRequired,
	handleLogin: PropTypes.func.isRequired,
  setShowMessage: PropTypes.func.isRequired,
	message: PropTypes.string.isRequired,
	isError: PropTypes.bool.isRequired,
};
