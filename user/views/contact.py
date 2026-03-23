from django.core.mail import send_mail
from django.conf import settings
from user.models import Contact


def process_contact(form, request):
    contato = form.save(commit=False)

    contato.ip_origem = request.META.get('REMOTE_ADDR')
    contato.user_agent = request.META.get('HTTP_USER_AGENT', '')[:500]

    contato.save()

    servicos_map = dict(Contact.SERVICO_CHOICES)
    servico_nome = servicos_map.get(contato.servico, 'Não informado')

    # ==============================
    # 📩 EMAIL INTERNO (VOCÊ)
    # ==============================
    corpo_email_admin = f"""
        <div style="background-color:#0f172a; padding:40px 20px; font-family:Arial, sans-serif; color:#e5e7eb;">
            
            <div style="max-width:600px; margin:auto; background:#111827; border-radius:16px; padding:30px; border:1px solid #1f2937;">
                
                <!-- Header -->
                <div style="text-align:center; margin-bottom:30px;">
                    <h1 style="color:#a855f7; margin-bottom:5px;">Bragga Dev</h1>
                    <p style="color:#9ca3af; font-size:14px;">Novo contato recebido</p>
                </div>

                <!-- Info principal -->
                <div style="margin-bottom:25px;">
                    <p><strong style="color:#c084fc;">Nome:</strong><br>{contato.nome}</p>
                    <p><strong style="color:#c084fc;">Email:</strong><br>{contato.email}</p>
                    <p><strong style="color:#c084fc;">Telefone:</strong><br>{contato.telefone}</p>
                    <p><strong style="color:#c084fc;">Assunto:</strong><br>{contato.assunto}</p>
                    <p><strong style="color:#c084fc;">Serviço:</strong><br>{servico_nome}</p>
                </div>

                <!-- Divider -->
                <hr style="border:0; border-top:1px solid #1f2937; margin:25px 0;">

                <!-- Mensagem -->
                <div style="margin-bottom:25px;">
                    <p style="color:#c084fc; font-weight:bold;">Mensagem:</p>
                    <div style="background:#0b1220; padding:15px; border-radius:10px; border:1px solid #1f2937;">
                        <p style="margin:0; line-height:1.6;">{contato.mensagem}</p>
                    </div>
                </div>

                <!-- Rodapé -->
                <div style="text-align:center; margin-top:30px;">
                    <p style="font-size:12px; color:#6b7280;">
                        IP: {contato.ip_origem}<br>
                        Enviado via site Bragga Dev
                    </p>
                </div>

            </div>

        </div>
        """

    send_mail(
        subject=f'[Bragga Dev] {contato.assunto} - {contato.nome}',
        message='',
        from_email=settings.DEFAULT_FROM_EMAIL,
        recipient_list=['bragawebdevelopment@gmail.com'],
        html_message=corpo_email_admin,
        fail_silently=False,
    )

    # ==============================
    # 📩 EMAIL AUTOMÁTICO (CLIENTE)
    # ==============================
    corpo_email_cliente = f"""
    <div style="font-family: Arial, sans-serif; background-color: #0f172a; padding: 30px; color: #e5e7eb;">
        
        <div style="max-width: 600px; margin: auto; background: #020617; border-radius: 12px; padding: 30px; border: 1px solid #1e293b;">
            
            <h1 style="color: #a855f7; text-align: center; margin-bottom: 20px;">
                BRAGGA DEV 🚀
            </h1>

            <h2 style="color: #ffffff;">Recebemos seu contato!</h2>

            <p style="margin-top: 15px; line-height: 1.6;">
                Olá <strong>{contato.nome}</strong>,
            </p>

            <p style="line-height: 1.6;">
                Recebemos sua mensagem com sucesso e já estamos analisando sua solicitação.
            </p>

            <div style="background:#0f172a; padding:15px; border-radius:8px; margin:20px 0;">
                <p><strong>Assunto:</strong> {contato.assunto}</p>
                <p><strong>Serviço:</strong> {servico_nome}</p>
            </div>

            <p style="line-height: 1.6;">
                Em breve entraremos em contato para atender sua demanda ou esclarecer suas dúvidas.
            </p>

            <p style="margin-top: 20px;">
                Muito obrigado pelo contato 🙌
            </p>

            <hr style="margin: 30px 0; border-color: #1e293b;">

            <p style="font-size: 12px; color: #64748b; text-align: center;">
                © 2026 Bragga Dev • Soluções em desenvolvimento web e inteligência artificial
            </p>

        </div>
    </div>
    """

    send_mail(
        subject="Recebemos sua mensagem • Bragga Dev",
        message='Recebemos sua mensagem. Em breve entraremos em contato.',
        from_email=settings.DEFAULT_FROM_EMAIL,
        recipient_list=[contato.email],
        html_message=corpo_email_cliente,
        fail_silently=False,
    )