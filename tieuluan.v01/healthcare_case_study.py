from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from typing import Dict, List
from uuid import uuid4


def generate_id(prefix: str) -> str:
    return f"{prefix}_{uuid4().hex[:8]}"


@dataclass
class Patient:
    patient_id: str
    full_name: str
    date_of_birth: str
    phone: str
    allergies: List[str] = field(default_factory=list)
    history: List[str] = field(default_factory=list)


@dataclass
class Appointment:
    appointment_id: str
    patient_id: str
    doctor_name: str
    room: str
    start_time: datetime
    status: str = "BOOKED"


@dataclass
class Encounter:
    encounter_id: str
    patient_id: str
    appointment_id: str
    symptoms: List[str]
    diagnosis: str = ""
    test_orders: List[str] = field(default_factory=list)
    test_results: Dict[str, str] = field(default_factory=dict)


@dataclass
class Prescription:
    prescription_id: str
    patient_id: str
    encounter_id: str
    items: Dict[str, str]


@dataclass
class Invoice:
    invoice_id: str
    patient_id: str
    encounter_id: str
    amount: float
    insurance_covered: float
    patient_payable: float
    status: str = "UNPAID"


class PatientService:
    def __init__(self) -> None:
        self._patients: Dict[str, Patient] = {}

    def create_patient(
        self,
        full_name: str,
        date_of_birth: str,
        phone: str,
        allergies: List[str] | None = None,
    ) -> Patient:
        patient = Patient(
            patient_id=generate_id("PAT"),
            full_name=full_name,
            date_of_birth=date_of_birth,
            phone=phone,
            allergies=allergies or [],
        )
        self._patients[patient.patient_id] = patient
        return patient

    def get_patient(self, patient_id: str) -> Patient:
        if patient_id not in self._patients:
            raise ValueError(f"Patient not found: {patient_id}")
        return self._patients[patient_id]


class AppointmentService:
    def __init__(self) -> None:
        self._appointments: Dict[str, Appointment] = {}

    def book_appointment(
        self,
        patient_id: str,
        doctor_name: str,
        room: str,
        start_time: datetime,
    ) -> Appointment:
        appointment = Appointment(
            appointment_id=generate_id("APM"),
            patient_id=patient_id,
            doctor_name=doctor_name,
            room=room,
            start_time=start_time,
        )
        self._appointments[appointment.appointment_id] = appointment
        return appointment

    def confirm(self, appointment_id: str) -> None:
        appointment = self._require_appointment(appointment_id)
        appointment.status = "CONFIRMED"

    def complete(self, appointment_id: str) -> None:
        appointment = self._require_appointment(appointment_id)
        appointment.status = "COMPLETED"

    def _require_appointment(self, appointment_id: str) -> Appointment:
        if appointment_id not in self._appointments:
            raise ValueError(f"Appointment not found: {appointment_id}")
        return self._appointments[appointment_id]


class EMRService:
    def __init__(self) -> None:
        self._encounters: Dict[str, Encounter] = {}

    def start_encounter(
        self,
        patient_id: str,
        appointment_id: str,
        symptoms: List[str],
    ) -> Encounter:
        encounter = Encounter(
            encounter_id=generate_id("ENC"),
            patient_id=patient_id,
            appointment_id=appointment_id,
            symptoms=symptoms,
        )
        self._encounters[encounter.encounter_id] = encounter
        return encounter

    def add_diagnosis(self, encounter_id: str, diagnosis: str) -> None:
        encounter = self._require_encounter(encounter_id)
        encounter.diagnosis = diagnosis

    def order_test(self, encounter_id: str, test_name: str) -> None:
        encounter = self._require_encounter(encounter_id)
        encounter.test_orders.append(test_name)

    def add_test_result(self, encounter_id: str, test_name: str, result: str) -> None:
        encounter = self._require_encounter(encounter_id)
        encounter.test_results[test_name] = result

    def _require_encounter(self, encounter_id: str) -> Encounter:
        if encounter_id not in self._encounters:
            raise ValueError(f"Encounter not found: {encounter_id}")
        return self._encounters[encounter_id]


class PharmacyService:
    def __init__(self) -> None:
        self._prescriptions: Dict[str, Prescription] = {}

    def issue_prescription(
        self,
        patient: Patient,
        encounter_id: str,
        items: Dict[str, str],
    ) -> Prescription:
        self._check_allergy_conflict(patient, items)
        prescription = Prescription(
            prescription_id=generate_id("RX"),
            patient_id=patient.patient_id,
            encounter_id=encounter_id,
            items=items,
        )
        self._prescriptions[prescription.prescription_id] = prescription
        return prescription

    def _check_allergy_conflict(self, patient: Patient, items: Dict[str, str]) -> None:
        meds = {name.lower() for name in items.keys()}
        allergies = {item.lower() for item in patient.allergies}
        conflict = meds.intersection(allergies)
        if conflict:
            joined = ", ".join(sorted(conflict))
            raise ValueError(f"Prescription conflicts with allergy: {joined}")


class BillingService:
    def __init__(self) -> None:
        self._invoices: Dict[str, Invoice] = {}

    def create_invoice(
        self,
        patient_id: str,
        encounter_id: str,
        amount: float,
        insurance_rate: float,
    ) -> Invoice:
        insurance_covered = round(amount * insurance_rate, 2)
        patient_payable = round(amount - insurance_covered, 2)
        invoice = Invoice(
            invoice_id=generate_id("INV"),
            patient_id=patient_id,
            encounter_id=encounter_id,
            amount=amount,
            insurance_covered=insurance_covered,
            patient_payable=patient_payable,
        )
        self._invoices[invoice.invoice_id] = invoice
        return invoice

    def pay(self, invoice_id: str) -> None:
        if invoice_id not in self._invoices:
            raise ValueError(f"Invoice not found: {invoice_id}")
        self._invoices[invoice_id].status = "PAID"


class NotificationService:
    def send_sms(self, phone: str, message: str) -> None:
        print(f"[SMS -> {phone}] {message}")


class HealthcareSystem:
    def __init__(self) -> None:
        self.patient_service = PatientService()
        self.appointment_service = AppointmentService()
        self.emr_service = EMRService()
        self.pharmacy_service = PharmacyService()
        self.billing_service = BillingService()
        self.notification_service = NotificationService()

    # End-to-end outpatient flow based on the case study analysis.
    def outpatient_visit_flow(self) -> None:
        patient = self.patient_service.create_patient(
            full_name="Nguyen Van A",
            date_of_birth="1998-07-12",
            phone="0901234567",
            allergies=["Penicillin"],
        )

        appointment = self.appointment_service.book_appointment(
            patient_id=patient.patient_id,
            doctor_name="Dr. Tran",
            room="P.201",
            start_time=datetime(2026, 4, 25, 9, 0),
        )
        self.appointment_service.confirm(appointment.appointment_id)
        self.notification_service.send_sms(
            patient.phone,
            f"Lich kham {appointment.start_time.strftime('%d/%m %H:%M')} da duoc xac nhan.",
        )

        encounter = self.emr_service.start_encounter(
            patient_id=patient.patient_id,
            appointment_id=appointment.appointment_id,
            symptoms=["Sot", "Ho", "Dau hong"],
        )
        self.emr_service.order_test(encounter.encounter_id, "CBC")
        self.emr_service.order_test(encounter.encounter_id, "CRP")
        self.emr_service.add_test_result(encounter.encounter_id, "CBC", "Binh thuong")
        self.emr_service.add_test_result(encounter.encounter_id, "CRP", "Tang nhe")
        self.emr_service.add_diagnosis(encounter.encounter_id, "Viem hong cap")

        prescription = self.pharmacy_service.issue_prescription(
            patient=patient,
            encounter_id=encounter.encounter_id,
            items={"Paracetamol": "500mg x 2 vien/ngay", "Vitamin C": "1 vien/ngay"},
        )

        invoice = self.billing_service.create_invoice(
            patient_id=patient.patient_id,
            encounter_id=encounter.encounter_id,
            amount=650000,
            insurance_rate=0.7,
        )
        self.billing_service.pay(invoice.invoice_id)
        self.appointment_service.complete(appointment.appointment_id)

        self._print_summary(patient, appointment, encounter, prescription, invoice)

    def _print_summary(
        self,
        patient: Patient,
        appointment: Appointment,
        encounter: Encounter,
        prescription: Prescription,
        invoice: Invoice,
    ) -> None:
        print("\n=== HEALTHCARE CASE STUDY SUMMARY ===")
        print(f"Patient: {patient.patient_id} - {patient.full_name}")
        print(f"Appointment: {appointment.appointment_id} | Status: {appointment.status}")
        print(f"Encounter: {encounter.encounter_id} | Diagnosis: {encounter.diagnosis}")
        print(f"Tests: {encounter.test_results}")
        print(f"Prescription: {prescription.items}")
        print(
            f"Invoice: {invoice.invoice_id} | Total: {invoice.amount:,.0f} | "
            f"Insurance: {invoice.insurance_covered:,.0f} | "
            f"Payable: {invoice.patient_payable:,.0f} | Status: {invoice.status}"
        )


if __name__ == "__main__":
    app = HealthcareSystem()
    app.outpatient_visit_flow()