class CalendarApp {
    constructor() {
        this.currentDate = new Date();
        this.selectedDate = null;
        this.selectedTime = null;
        this.appointments = JSON.parse(localStorage.getItem('appointments')) || [];
        this.timeSlots = [
            '09:00', '09:30', '10:00', '10:30', '11:00', '11:30',
            '14:00', '14:30', '15:00', '15:30', '16:00', '16:30', '17:00'
        ];
        
        this.init();
    }

    init() {
        this.renderCalendar();
        this.renderAppointments();
        this.bindEvents();
    }

    bindEvents() {
        document.getElementById('prevMonth').addEventListener('click', () => {
            this.currentDate.setMonth(this.currentDate.getMonth() - 1);
            this.renderCalendar();
        });

        document.getElementById('nextMonth').addEventListener('click', () => {
            this.currentDate.setMonth(this.currentDate.getMonth() + 1);
            this.renderCalendar();
        });

        document.getElementById('cancelBooking').addEventListener('click', () => {
            this.hideBookingForm();
        });

        document.getElementById('confirmBooking').addEventListener('click', () => {
            this.confirmBooking();
        });
    }

    renderCalendar() {
        const calendar = document.getElementById('calendar');
        const monthYear = document.getElementById('monthYear');
        
        const year = this.currentDate.getFullYear();
        const month = this.currentDate.getMonth();
        
        monthYear.textContent = new Date(year, month).toLocaleDateString('es-ES', {
            month: 'long',
            year: 'numeric'
        });

        const firstDay = new Date(year, month, 1);
        const lastDay = new Date(year, month + 1, 0);
        const startDate = new Date(firstDay);
        startDate.setDate(startDate.getDate() - firstDay.getDay());

        calendar.innerHTML = '';

        // Day headers
        const dayHeaders = ['Dom', 'Lun', 'Mar', 'Mié', 'Jue', 'Vie', 'Sáb'];
        dayHeaders.forEach(day => {
            const header = document.createElement('div');
            header.className = 'day-header';
            header.textContent = day;
            calendar.appendChild(header);
        });

        // Calendar days
        const today = new Date();
        for (let i = 0; i < 42; i++) {
            const cellDate = new Date(startDate);
            cellDate.setDate(startDate.getDate() + i);
            
            const cell = document.createElement('div');
            cell.className = 'day-cell';
            
            if (cellDate.getMonth() !== month) {
                cell.classList.add('other-month');
            }
            
            if (cellDate.toDateString() === today.toDateString()) {
                cell.classList.add('today');
            }

            const dayNumber = document.createElement('div');
            dayNumber.className = 'day-number';
            dayNumber.textContent = cellDate.getDate();
            cell.appendChild(dayNumber);

            // Only allow future dates
            if (cellDate >= today && cellDate.getMonth() === month) {
                cell.addEventListener('click', () => {
                    this.selectDate(cellDate);
                });
            } else if (cellDate < today) {
                cell.style.opacity = '0.3';
                cell.style.cursor = 'not-allowed';
            }

            calendar.appendChild(cell);
        }
    }

    selectDate(date) {
        // Remove previous selection
        document.querySelectorAll('.day-cell.selected').forEach(cell => {
            cell.classList.remove('selected');
        });

        event.currentTarget.classList.add('selected');
        this.selectedDate = new Date(date);

        // Guardar fecha en el input hidden en formato YYYY-MM-DD
        const fechaISO = this.selectedDate.toISOString().split('T')[0];
        document.getElementById('inputFecha').value = fechaISO;

        this.showTimeSlots();
    }

    selectTimeSlot(time, slotElement) {
        // Remove previous selection
        document.querySelectorAll('.time-slot.selected').forEach(slot => {
            slot.classList.remove('selected');
        });

        slotElement.classList.add('selected');
        this.selectedTime = time;

        // Guardar hora en el input hidden
        document.getElementById('inputHora').value = this.selectedTime;

        this.showBookingForm();
    }

    showTimeSlots() {
        const timeSlots = document.getElementById('timeSlots');
        const selectedDate = document.getElementById('selectedDate');
        const slotsGrid = document.getElementById('slotsGrid');

        selectedDate.textContent = `Horarios disponibles para ${this.selectedDate.toLocaleDateString('es-ES', {
            weekday: 'long',
            year: 'numeric',
            month: 'long',
            day: 'numeric'
        })}`;

        slotsGrid.innerHTML = '';

        this.timeSlots.forEach(time => {
            const slot = document.createElement('div');
            slot.className = 'time-slot';
            slot.textContent = time;

            // Check if slot is occupied
            const isOccupied = this.appointments.some(apt => 
                apt.date === this.selectedDate.toDateString() && apt.time === time
            );

            if (isOccupied) {
                slot.classList.add('occupied');
                slot.textContent += ' (Ocupado)';
            } else {
                slot.addEventListener('click', () => {
                    this.selectTimeSlot(time, slot);
                });
            }

            slotsGrid.appendChild(slot);
        });

        timeSlots.classList.add('active');
    }

    showBookingForm() {
        const bookingForm = document.getElementById('bookingForm');
        bookingForm.classList.add('active');
        document.getElementById('clientName').focus();
    }

    hideBookingForm() {
        const bookingForm = document.getElementById('bookingForm');
        bookingForm.classList.remove('selected');
        document.getElementById('clientName').value = '';
        document.getElementById('clientPhone').value = '';
        
        // Remove time slot selection
        document.querySelectorAll('.time-slot.selected').forEach(slot => {
            slot.classList.remove('selected');
        });
        
        this.selectedTime = null;
    }

    confirmBooking() {
        const name = document.getElementById('clientName').value.trim();
        const phone = document.getElementById('clientPhone').value.trim();

        if (!name || !phone) {
            alert('Por favor completa todos los campos');
            return;
        }

        const appointment = {
            id: Date.now(),
            date: this.selectedDate.toDateString(),
            time: this.selectedTime,
            name: name,
            phone: phone
        };

        this.appointments.push(appointment);
        localStorage.setItem('appointments', JSON.stringify(this.appointments));

        alert('¡Turno reservado exitosamente!');
        
        this.hideBookingForm();
        this.showTimeSlots(); // Refresh time slots
        this.renderAppointments();
    }

    renderAppointments() {
        const appointmentsList = document.getElementById('appointmentsList');
        
        if (this.appointments.length === 0) {
            appointmentsList.innerHTML = '<p style="color: #666; font-style: italic;">No hay turnos reservados</p>';
            return;
        }

        // Sort appointments by date and time
        const sortedAppointments = this.appointments.sort((a, b) => {
            const dateA = new Date(a.date + ' ' + a.time);
            const dateB = new Date(b.date + ' ' + b.time);
            return dateA - dateB;
        });

        appointmentsList.innerHTML = sortedAppointments.map(apt => `
            <div class="appointment-item">
                <div class="appointment-info">
                    <div class="appointment-date">
                        ${new Date(apt.date).toLocaleDateString('es-ES', {
                            weekday: 'long',
                            year: 'numeric',
                            month: 'long',
                            day: 'numeric'
                        })} - ${apt.time}
                    </div>
                    <div class="appointment-name">${apt.name} - ${apt.phone}</div>
                </div>
                <button class="btn-cancel" onclick="calendar.cancelAppointment(${apt.id})">
                    Cancelar
                </button>
            </div>
        `).join('');
    }

    cancelAppointment(id) {
        if (confirm('¿Estás seguro de que quieres cancelar este turno?')) {
            this.appointments = this.appointments.filter(apt => apt.id !== id);
            localStorage.setItem('appointments', JSON.stringify(this.appointments));
            this.renderAppointments();
            
            // Refresh time slots if showing
            if (this.selectedDate) {
                this.showTimeSlots();
            }
        }
    }
}

// Initialize the calendar
const calendar = new CalendarApp();