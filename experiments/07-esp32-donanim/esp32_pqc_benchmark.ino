#include <Arduino.h>
#include <esp_cpu.h>
#include <soc/soc.h>
#include <soc/rtc_cntl_reg.h>

#define N 256
#define Q 3329
#define HALF_Q 1664
#define NUM_RUNS 100

int16_t a[N];
int16_t s[N];
int16_t out_school[N];
int16_t out_kronecker[N];

static inline int16_t barrett_reduce(int32_t val) {
    int32_t r = val % Q;
    if (r > HALF_Q) r -= Q;
    if (r < -HALF_Q) r += Q;
    return (int16_t)r;
}

void schoolbook_negacyclic(const int16_t* poly_a, const int16_t* poly_s, int16_t* res) {
    int32_t c[2 * N - 1] = {0};
    for (int i = 0; i < N; i++) {
        for (int j = 0; j < N; j++) {
            c[i + j] += (int32_t)poly_a[i] * poly_s[j];
        }
    }
    for (int k = 0; k < N; k++) {
        int32_t val = c[k];
        if (k + N < 2 * N - 1) {
            val -= c[k + N];
        }
        res[k] = barrett_reduce(val);
    }
}

void kronecker_comba_24bit(const int16_t* poly_a, const int16_t* poly_s, int16_t* res) {
    for (int k = 0; k < N; k++) {
        int32_t acc = 0;
        for (int i = 0; i <= k; i++) {
            acc += (int32_t)poly_a[i] * poly_s[k - i];
        }
        for (int i = k + 1; i < N; i++) {
            acc -= (int32_t)poly_a[i] * poly_s[k + N - i];
        }
        res[k] = barrett_reduce(acc);
    }
}

void setup() {
    WRITE_PERI_REG(RTC_CNTL_BROWN_OUT_REG, 0); // BOD kapat
    setCpuFrequencyMhz(80); // Kararlılık ve düşük akım için 80 MHz

    Serial.begin(115200);
    delay(2000);
    Serial.println();
    Serial.println("========================================================");
    Serial.println("   TUBITAK 2204-A: ESP32 PQC POLINOM CARPIMI BENCHMARK   ");
    Serial.println("========================================================");
    Serial.printf("CPU Frekansi: %u MHz\n", getCpuFrequencyMhz());
    Serial.printf("Parametreler: N = %d, q = %d, Calistirma Sayisi = %d\n", N, Q, NUM_RUNS);

    for (int i = 0; i < N; i++) {
        a[i] = (int16_t)(random(-HALF_Q, HALF_Q + 1));
        s[i] = (int16_t)(random(-3, 4));
    }

    schoolbook_negacyclic(a, s, out_school);
    kronecker_comba_24bit(a, s, out_kronecker);

    bool match = true;
    for (int i = 0; i < N; i++) {
        if (out_school[i] != out_kronecker[i]) {
            match = false;
            break;
        }
    }
    Serial.printf("[DOGRULUK]: %s\n", match ? "BASARILI (Sonuclar Birebir Eslesiyor %100)" : "HATALI!");

    uint32_t total_cycles_school = 0;
    uint32_t total_us_school = 0;
    for (int r = 0; r < NUM_RUNS; r++) {
        uint32_t start_c = esp_cpu_get_cycle_count();
        uint32_t start_t = micros();
        schoolbook_negacyclic(a, s, out_school);
        uint32_t end_t = micros();
        uint32_t end_c = esp_cpu_get_cycle_count();
        total_cycles_school += (end_c - start_c);
        total_us_school += (end_t - start_t);
    }

    uint32_t total_cycles_kron = 0;
    uint32_t total_us_kron = 0;
    for (int r = 0; r < NUM_RUNS; r++) {
        uint32_t start_c = esp_cpu_get_cycle_count();
        uint32_t start_t = micros();
        kronecker_comba_24bit(a, s, out_kronecker);
        uint32_t end_t = micros();
        uint32_t end_c = esp_cpu_get_cycle_count();
        total_cycles_kron += (end_c - start_c);
        total_us_kron += (end_t - start_t);
    }

    float avg_cycles_school = (float)total_cycles_school / NUM_RUNS;
    float avg_us_school = (float)total_us_school / NUM_RUNS;
    float avg_cycles_kron = (float)total_cycles_kron / NUM_RUNS;
    float avg_us_kron = (float)total_us_kron / NUM_RUNS;
    float speedup = avg_cycles_school / avg_cycles_kron;

    Serial.println("----------------- BENCHMARK SONUCLARI ------------------");
    Serial.printf("1. Standart Okul Yontemi:        %.2f cevril (%.2f us)\n", avg_cycles_school, avg_us_school);
    Serial.printf("2. Merkezlenmis Kronecker/Comba: %.2f cevril (%.2f us)\n", avg_cycles_kron, avg_us_kron);
    Serial.println("--------------------------------------------------------");
    Serial.printf(">>> HIZLANMA ORANI (SPEEDUP):     %.2fx KAT HIZLI <<<\n", speedup);
    Serial.printf(">>> CEVRIM TASARRUFU:             %%%.2f <<<\n", (1.0f - (avg_cycles_kron / avg_cycles_school)) * 100.0f);
    Serial.println("========================================================");
}

void loop() {
    delay(5000);
}
