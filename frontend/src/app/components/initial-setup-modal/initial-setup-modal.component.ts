import { Component, Output, EventEmitter, signal, computed } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { Category, TipoGasto, TipoCategoria } from '../../models';
import { PeriodService } from '../../services/period.service';
import { CategoryService } from '../../services/category.service';
import { ExpenseService } from '../../services/expense.service';
import { AporteService } from '../../services/aporte.service';

interface TempExpense {
  nombre: string;
  monto: number;
  es_permanente: boolean;
  periodos_restantes?: number;
  descripcion?: string;
}

interface TempAporte {
  nombre: string;
  monto: number;
  es_fijo: boolean;
  descripcion?: string;
}

@Component({
  selector: 'app-initial-setup-modal',
  standalone: true,
  imports: [CommonModule, FormsModule],
  templateUrl: './initial-setup-modal.component.html',
  styleUrl: './initial-setup-modal.component.css'
})
export class InitialSetupModalComponent {
  @Output() close = new EventEmitter<void>();
  @Output() complete = new EventEmitter<void>();

  // Control de pasos
  currentStep = signal<number>(1);
  totalSteps = 5;

  // Paso 1: Datos básicos
  sueldo = signal<number>(0);
  creditoAnterior = signal<number>(0);

  // Paso 2: Ahorro
  gastosFijosAhorro = signal<TempExpense[]>([]);
  aportesAhorro = signal<TempAporte[]>([]);

  // Paso 3: Arriendo
  gastosFijosArriendo = signal<TempExpense[]>([]);
  aportesArriendo = signal<TempAporte[]>([]);

  // Paso 4: Crédito
  metaCredito = signal<number>(0);
  gastosFijosCredito = signal<TempExpense[]>([]);

  // Formularios temporales
  showExpenseForm = signal<boolean>(false);
  showAporteForm = signal<boolean>(false);

  expenseForm = {
    nombre: '',
    monto: 0,
    es_permanente: true,
    periodos_restantes: 0,
    descripcion: ''
  };

  aporteForm = {
    nombre: '',
    monto: 0,
    es_fijo: true,
    descripcion: ''
  };

  // Categorías
  categories = computed(() => this.categoryService.categories());

  ahorroCategory = computed(() =>
    this.categories().find(c => c.slug === TipoCategoria.AHORRO)
  );

  arriendoCategory = computed(() =>
    this.categories().find(c => c.slug === TipoCategoria.ARRIENDO)
  );

  creditoCategory = computed(() =>
    this.categories().find(c => c.slug === TipoCategoria.CREDITO)
  );

  // Cálculos
  totalGastosFijosAhorro = computed(() =>
    this.gastosFijosAhorro().reduce((sum, e) => sum + e.monto, 0)
  );

  totalAportesAhorro = computed(() =>
    this.aportesAhorro().reduce((sum, a) => sum + a.monto, 0)
  );

  totalRealAhorro = computed(() =>
    this.totalGastosFijosAhorro() - this.totalAportesAhorro()
  );

  // Meta de ahorro = total real de ahorro (calculado)
  metaAhorro = computed(() => this.totalRealAhorro());

  totalGastosFijosArriendo = computed(() =>
    this.gastosFijosArriendo().reduce((sum, e) => sum + e.monto, 0)
  );

  totalAportesArriendo = computed(() =>
    this.aportesArriendo().reduce((sum, a) => sum + a.monto, 0)
  );

  totalRealArriendo = computed(() =>
    this.totalGastosFijosArriendo() - this.totalAportesArriendo()
  );

  // Meta de arriendo = total real de arriendo (calculado)
  metaArriendo = computed(() => this.totalRealArriendo());

  totalGastosFijosCredito = computed(() =>
    this.gastosFijosCredito().reduce((sum, e) => sum + e.monto, 0)
  );

  creditoDisponible = computed(() =>
    this.metaCredito() - this.totalGastosFijosCredito()
  );

  liquidezCalculada = computed(() =>
    this.sueldo() - this.metaAhorro() - this.totalRealArriendo() - this.creditoAnterior()
  );

  isLoading = signal<boolean>(false);

  constructor(
    private periodService: PeriodService,
    private categoryService: CategoryService,
    private expenseService: ExpenseService,
    private aporteService: AporteService
  ) {}

  // Navegación de pasos
  nextStep() {
    if (this.currentStep() < this.totalSteps) {
      this.currentStep.update(s => s + 1);
    }
  }

  prevStep() {
    if (this.currentStep() > 1) {
      this.currentStep.update(s => s - 1);
    }
  }

  canProceed(): boolean {
    switch (this.currentStep()) {
      case 1:
        return this.sueldo() > 0;
      case 2:
        return this.metaAhorro() >= 0;
      case 3:
        return this.metaArriendo() >= 0;
      case 4:
        return this.metaCredito() >= 0;
      case 5:
        return true;
      default:
        return false;
    }
  }

  // Gestión de gastos temporales
  openExpenseForm() {
    this.resetExpenseForm();
    this.showExpenseForm.set(true);
  }

  resetExpenseForm() {
    this.expenseForm = {
      nombre: '',
      monto: 0,
      es_permanente: true,
      periodos_restantes: 0,
      descripcion: ''
    };
  }

  cancelExpenseForm() {
    this.showExpenseForm.set(false);
  }

  addExpense() {
    if (!this.expenseForm.nombre || this.expenseForm.monto <= 0) {
      alert('Completa nombre y monto');
      return;
    }

    const expense: TempExpense = {
      nombre: this.expenseForm.nombre,
      monto: this.expenseForm.monto,
      es_permanente: this.expenseForm.es_permanente,
      periodos_restantes: this.expenseForm.es_permanente ? undefined : this.expenseForm.periodos_restantes,
      descripcion: this.expenseForm.descripcion || undefined
    };

    const step = this.currentStep();
    if (step === 2) {
      this.gastosFijosAhorro.update(arr => [...arr, expense]);
    } else if (step === 3) {
      this.gastosFijosArriendo.update(arr => [...arr, expense]);
    } else if (step === 4) {
      this.gastosFijosCredito.update(arr => [...arr, expense]);
    }

    this.showExpenseForm.set(false);
    this.resetExpenseForm();
  }

  removeExpense(index: number) {
    const step = this.currentStep();
    if (step === 2) {
      this.gastosFijosAhorro.update(arr => arr.filter((_, i) => i !== index));
    } else if (step === 3) {
      this.gastosFijosArriendo.update(arr => arr.filter((_, i) => i !== index));
    } else if (step === 4) {
      this.gastosFijosCredito.update(arr => arr.filter((_, i) => i !== index));
    }
  }

  // Gestión de aportes temporales
  openAporteForm() {
    this.resetAporteForm();
    this.showAporteForm.set(true);
  }

  resetAporteForm() {
    this.aporteForm = {
      nombre: '',
      monto: 0,
      es_fijo: true,
      descripcion: ''
    };
  }

  cancelAporteForm() {
    this.showAporteForm.set(false);
  }

  addAporte() {
    if (!this.aporteForm.nombre || this.aporteForm.monto <= 0) {
      alert('Completa nombre y monto');
      return;
    }

    const aporte: TempAporte = {
      nombre: this.aporteForm.nombre,
      monto: this.aporteForm.monto,
      es_fijo: this.aporteForm.es_fijo,
      descripcion: this.aporteForm.descripcion || undefined
    };

    const step = this.currentStep();
    if (step === 2) {
      this.aportesAhorro.update(arr => [...arr, aporte]);
    } else if (step === 3) {
      this.aportesArriendo.update(arr => [...arr, aporte]);
    }

    this.showAporteForm.set(false);
    this.resetAporteForm();
  }

  removeAporte(index: number) {
    const step = this.currentStep();
    if (step === 2) {
      this.aportesAhorro.update(arr => arr.filter((_, i) => i !== index));
    } else if (step === 3) {
      this.aportesArriendo.update(arr => arr.filter((_, i) => i !== index));
    }
  }

  // Guardar configuración completa
  async saveConfiguration() {
    this.isLoading.set(true);

    try {
      // 1. Obtener períodos activos
      const mensualPeriod = this.periodService.activeMensualPeriod();
      const creditPeriod = this.periodService.activeCreditPeriod();

      if (!mensualPeriod || !creditPeriod) {
        throw new Error('No se encontraron períodos activos');
      }

      // 2. Actualizar período mensual con sueldo solamente
      // NOTA: Ahorro y Arriendo NO tienen meta, solo Crédito tiene meta
      await this.periodService.updatePeriod(mensualPeriod._id, {
        sueldo: this.sueldo()
      }).toPromise();

      // 2b. Actualizar período de crédito con meta de crédito
      await this.periodService.updatePeriod(creditPeriod._id, {
        metas_categorias: {
          credito_usable: this.metaCredito()
        }
      }).toPromise();

      // 3. Actualizar período de crédito con deuda anterior
      await this.periodService.updatePeriod(creditPeriod._id, {
        total_gastado: this.creditoAnterior()
      }).toPromise();

      // 4. Crear gastos fijos de Ahorro
      await this.createExpensesForCategory(
        mensualPeriod._id,
        this.ahorroCategory()?._id!,
        this.gastosFijosAhorro()
      );

      // 5. Crear aportes de Ahorro
      await this.createAportesForCategory(
        mensualPeriod._id,
        this.ahorroCategory()?._id!,
        this.aportesAhorro()
      );

      // 6. Crear gastos fijos de Arriendo
      await this.createExpensesForCategory(
        mensualPeriod._id,
        this.arriendoCategory()?._id!,
        this.gastosFijosArriendo()
      );

      // 7. Crear aportes de Arriendo
      await this.createAportesForCategory(
        mensualPeriod._id,
        this.arriendoCategory()?._id!,
        this.aportesArriendo()
      );

      // 8. Crear gastos fijos de Crédito
      await this.createExpensesForCategory(
        creditPeriod._id,
        this.creditoCategory()?._id!,
        this.gastosFijosCredito()
      );

      this.isLoading.set(false);
      this.complete.emit();
    } catch (error) {
      console.error('Error al guardar configuración:', error);
      alert('Error al guardar la configuración');
      this.isLoading.set(false);
    }
  }

  private async createExpensesForCategory(
    periodoId: string,
    categoriaId: string,
    expenses: TempExpense[]
  ) {
    for (const expense of expenses) {
      await this.expenseService.createExpense(periodoId, {
        nombre: expense.nombre,
        monto: expense.monto,
        categoria_id: categoriaId,
        tipo: TipoGasto.FIJO,
        es_permanente: expense.es_permanente,
        periodos_restantes: expense.periodos_restantes,
        descripcion: expense.descripcion
      }).toPromise();
    }
  }

  private async createAportesForCategory(
    periodoId: string,
    categoriaId: string,
    aportes: TempAporte[]
  ) {
    for (const aporte of aportes) {
      await this.aporteService.createAporte(periodoId, {
        nombre: aporte.nombre,
        monto: aporte.monto,
        categoria_id: categoriaId,
        es_fijo: aporte.es_fijo,
        descripcion: aporte.descripcion
      }).toPromise();
    }
  }

  onClose() {
    this.close.emit();
  }

  // Helpers
  formatCurrency(value: number): string {
    return new Intl.NumberFormat('es-CL', {
      style: 'currency',
      currency: 'CLP',
      minimumFractionDigits: 0
    }).format(value);
  }

  getExpenseLabel(expense: TempExpense): string {
    if (expense.es_permanente) {
      return `${expense.nombre} (Permanente)`;
    } else {
      return `${expense.nombre} (${expense.periodos_restantes} cuotas)`;
    }
  }

  getAporteLabel(aporte: TempAporte): string {
    return aporte.es_fijo ? `${aporte.nombre} (Fijo)` : aporte.nombre;
  }

  getCurrentStepExpenses(): TempExpense[] {
    const step = this.currentStep();
    if (step === 2) return this.gastosFijosAhorro();
    if (step === 3) return this.gastosFijosArriendo();
    if (step === 4) return this.gastosFijosCredito();
    return [];
  }

  getCurrentStepAportes(): TempAporte[] {
    const step = this.currentStep();
    if (step === 2) return this.aportesAhorro();
    if (step === 3) return this.aportesArriendo();
    return [];
  }

  canAddAportes(): boolean {
    return this.currentStep() === 2 || this.currentStep() === 3;
  }
}
