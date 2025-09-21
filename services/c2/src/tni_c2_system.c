#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <unistd.h>
#include <sys/types.h>
#include <sys/socket.h>
#include <netinet/in.h>
#include <arpa/inet.h>
#include <signal.h>
#include <dlfcn.h>
#include <malloc.h>

char *command_buffer = NULL;
char *classified_data = NULL;
char *heap_chunk = NULL;

char global_buffer[256];

void (*function_ptr)(void) = NULL;

struct tni_officer {
    char name[32];
    char rank[16]; 
    char clearance[8];
    int access_level;
    char *classified_ptr;
};

struct tni_officer officers[10];
int officer_count = 0;

void print_banner() {
    printf("\n");
    printf("╔══════════════════════════════════════════════════════════════╗\n");
    printf("║                   🇮🇩 TNI COMMAND CENTER 🇮🇩                   ║\n");  
    printf("║                   SISTEM KOMANDO TERPADU                     ║\n");
    printf("║                      TINGKAT RAHASIA                         ║\n");
    printf("╚══════════════════════════════════════════════════════════════╝\n");
    printf("\n");
}

void process_command(char *input) {
    char local_buffer[128];
    char format_buffer[256];
    char *heap_buffer;
    
    printf("C2 Log: ");
    printf(input);
    printf("\n");
    
    printf("Memproses komando: ");
    if (strlen(input) < sizeof(local_buffer)) {  
        strcpy(local_buffer, input);
    } else {
        strncpy(local_buffer, input, sizeof(local_buffer) - 1);
        local_buffer[sizeof(local_buffer) - 1] = '\0';
    }
    printf("%s\n", local_buffer);
    
    heap_buffer = malloc(strlen(input) + 1); 
    strcpy(heap_buffer, input);
    
    if (command_buffer) {
        free(command_buffer);
    }
    command_buffer = heap_buffer;
    
    if (strlen(input) > 10) {
        char *vuln_buffer = malloc(32); 
        strcpy(vuln_buffer, input);     
        free(vuln_buffer);
    }
}

void exec_shell() {
    printf("PERINGATAN: Shell akses darurat C2 diaktifkan!\n");
    system("/bin/sh");
}

void read_classified() {
    FILE *fp = fopen("clearance_token", "r");
    if (fp) {
        char token[64];
        fgets(token, sizeof(token), fp);
        printf("CLASSIFIED TOKEN: %s", token);
        fclose(fp);
    }
}

void manage_classified_data() {
    char input[512];
    
    printf("C2: Masukkan data rahasia: ");
    fgets(input, sizeof(input), stdin);
    
    if (classified_data) {
        free(classified_data);
    }
    
    classified_data = malloc(strlen(input) + 1);
    strcpy(classified_data, input);
    
    printf("Data tersimpan di alamat: %p\n", classified_data);
    
    free(classified_data);
    printf("Data masih dapat diakses: %s", classified_data);
    
}

void add_officer() {
    char name_input[100];
    char rank_input[50];
    
    if (officer_count >= 10) {
        printf("Database penuh!\n");
        return;
    }
    
    printf("Nama perwira: ");
    fgets(name_input, sizeof(name_input), stdin);
    
    printf("Pangkat: ");
    fgets(rank_input, sizeof(rank_input), stdin);
    
    strcpy(officers[officer_count].name, name_input);
    strcpy(officers[officer_count].rank, rank_input);
    
    officers[officer_count].access_level = 1;
    officers[officer_count].classified_ptr = malloc(256);
    
    officer_count++;
}

void system_diagnostics() {
    char diag_buffer[512];
    
    printf("C2 Diagnostics - Masukkan parameter: ");
    fgets(diag_buffer, sizeof(diag_buffer), stdin);
    
    for (int i = 0; i < 5; i++) {
        printf("Diagnostic %d: ", i);
        printf(diag_buffer);
        printf("\n");
    }
}

void network_interface() {
    char packet_data[1024];
    char processed_packet[256];
    
    printf("Network Interface - Masukkan data paket: ");
    fgets(packet_data, sizeof(packet_data), stdin);
    
    if (strlen(packet_data) < sizeof(processed_packet)) {
        strcpy(processed_packet, packet_data);
    } else {
        strncpy(processed_packet, packet_data, sizeof(processed_packet) - 1);
        processed_packet[sizeof(processed_packet) - 1] = '\0';
    }
    
    printf("Paket diproses: ");
    printf(processed_packet);
    printf("\n");
    
    function_ptr = (void(*)())processed_packet;
}

void command_loop() {
    char input[1024];
    
    print_banner();
    printf("C2 System Online - Ketik 'help' untuk bantuan\n");
    
    while (1) {
        printf("C2> ");
        fflush(stdout);
        
        if (!fgets(input, sizeof(input), stdin)) {
            break;
        }
        
        input[strcspn(input, "\n")] = 0;
        
        if (strlen(input) == 0) continue;
        
        if (strcmp(input, "help") == 0) {
            printf("Available commands:\n");
            printf("  process <data>     - Process command data\n");
            printf("  classified         - Manage classified data\n");
            printf("  officer            - Add officer data\n");
            printf("  diagnostic         - Run system diagnostics\n");
            printf("  network            - Network interface\n");
            printf("  shell              - Emergency shell (restricted)\n");
            printf("  exit               - Keluar dari sistem\n");
        }
        else if (strncmp(input, "process ", 8) == 0) {
            process_command(input + 8);
        }
        else if (strcmp(input, "classified") == 0) {
            manage_classified_data();
        }
        else if (strcmp(input, "officer") == 0) {
            add_officer();
        }
        else if (strcmp(input, "diagnostic") == 0) {
            system_diagnostics();
        }
        else if (strcmp(input, "network") == 0) {
            network_interface();
        }
        else if (strcmp(input, "shell") == 0) {
            printf("AKSES DITOLAK: Clearance level tidak mencukupi\n");
            printf("Gunakan exploitasi untuk mendapatkan akses shell!\n");
        }
        else if (strcmp(input, "exit") == 0) {
            printf("C2 System Shutdown...\n");
            break;
        }
        else {
            printf("Komando tidak dikenali: %s\n", input);
            printf(input);
            printf("\n");
        }
    }
}

int main(int argc, char **argv) {
    setvbuf(stdout, NULL, _IONBF, 0);
    setvbuf(stdin, NULL, _IONBF, 0);
    setvbuf(stderr, NULL, _IONBF, 0);
    
    signal(SIGSEGV, SIG_DFL);
    signal(SIGPIPE, SIG_IGN);
    
    alarm(300);
    
    command_loop();
    
    return 0;
}

void hidden_backdoor() {
    printf("🚪 BACKDOOR DITEMUKAN!\n");
    system("cat clearance_token");
}

void secret_function() {
    printf("Secret function called!\n");
    exec_shell();
}