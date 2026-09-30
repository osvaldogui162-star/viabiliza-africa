export type LegalSection = {
  title: string;
  paragraphs: string[];
};

export type LegalDocument = {
  title: string;
  subtitle: string;
  version: string;
  lastUpdated: string;
  sections: LegalSection[];
};

export const TERMS_PT: LegalDocument = {
  title: "Termos de Utilização",
  subtitle: "ViabilizA+ África — plataforma de estudos de viabilidade económica e financeira",
  version: "2026-01",
  lastUpdated: "Janeiro de 2026",
  sections: [
    {
      title: "1. Aceitação",
      paragraphs: [
        "Ao criar conta ou utilizar a ViabilizA+ África («Plataforma»), o utilizador declara ter lido, compreendido e aceite estes Termos de Utilização e a Política de Privacidade.",
        "Se não concordar, não deve utilizar a Plataforma.",
      ],
    },
    {
      title: "2. Serviço",
      paragraphs: [
        "A Plataforma disponibiliza ferramentas para criação de projectos, ingestão de dados, análise financeira, simulações, relatórios e colaboração entre equipas.",
        "Os resultados produzidos têm carácter de apoio à decisão e não substituem pareceres jurídicos, fiscais ou de auditoria independente.",
      ],
    },
    {
      title: "3. Contas e acesso",
      paragraphs: [
        "O registo pode estar sujeito a convite ou aprovação administrativa, conforme a política activa da organização.",
        "O utilizador é responsável pela confidencialidade das credenciais e por toda a actividade realizada na sua conta.",
        "Contas inactivas ou que violem estes termos podem ser suspensas ou encerradas.",
      ],
    },
    {
      title: "4. Planos e pagamentos",
      paragraphs: [
        "Funcionalidades, limites de projectos, colaboradores e integrações dependem do plano de subscrição activo.",
        "Preços, ciclos de facturação e condições comerciais são apresentados na página de planos e confirmados no checkout.",
        "O não pagamento pode implicar downgrade ou restrição de funcionalidades.",
      ],
    },
    {
      title: "5. Dados e conteúdos do utilizador",
      paragraphs: [
        "O utilizador mantém a titularidade dos dados e documentos que carrega (projectos, orçamentos, relatórios, mensagens).",
        "Concede à Plataforma licença limitada para processar esses conteúdos exclusivamente para prestar o serviço, incluindo cópias de segurança e exportações solicitadas.",
        "É proibido carregar dados ilícitos, difamatórios ou que infrinjam direitos de terceiros.",
      ],
    },
    {
      title: "6. Uso aceitável",
      paragraphs: [
        "É proibido tentar aceder a áreas ou dados de outros utilizadores sem autorização, interferir com a segurança da Plataforma, efectuar engenharia inversa ou usar a Plataforma para fins fraudulentos.",
        "A partilha de projectos deve respeitar acordos de confidencialidade aplicáveis entre as partes.",
      ],
    },
    {
      title: "7. Propriedade intelectual",
      paragraphs: [
        "A marca, interface, software e documentação da Plataforma são propriedade da ViabilizA+ África ou dos seus licenciadores.",
        "Nada nestes termos transfere esses direitos ao utilizador, excepto o direito de uso conforme o plano contratado.",
      ],
    },
    {
      title: "8. Limitação de responsabilidade",
      paragraphs: [
        "A Plataforma é fornecida «tal como está», com esforços razoáveis de disponibilidade e exactidão.",
        "Na medida permitida pela lei aplicável, não nos responsabilizamos por perdas indirectas, lucros cessantes ou decisões tomadas com base exclusiva nos outputs da Plataforma.",
      ],
    },
    {
      title: "9. Alterações",
      paragraphs: [
        "Podemos actualizar estes termos. A versão vigente será indicada pelo identificador de versão (ex.: 2026-01) e comunicada quando relevante.",
        "O uso continuado após alterações constitui aceitação da nova versão, salvo quando a lei exija novo consentimento.",
      ],
    },
    {
      title: "10. Lei aplicável e contacto",
      paragraphs: [
        "Estes termos regem-se pela lei da República de Angola, sem prejuízo de normas imperativas de protecção de consumidores quando aplicáveis.",
        "Questões sobre estes termos: comercial@viabiliza.africa",
      ],
    },
  ],
};

export const TERMS_EN: LegalDocument = {
  title: "Terms of Use",
  subtitle: "ViabilizA+ Africa — economic and financial feasibility study platform",
  version: "2026-01",
  lastUpdated: "January 2026",
  sections: [
    {
      title: "1. Acceptance",
      paragraphs: [
        "By creating an account or using ViabilizA+ Africa (the “Platform”), you confirm that you have read, understood, and accepted these Terms of Use and the Privacy Policy.",
        "If you do not agree, do not use the Platform.",
      ],
    },
    {
      title: "2. Service",
      paragraphs: [
        "The Platform provides tools to create projects, ingest data, run financial analysis, simulations, reports, and team collaboration.",
        "Outputs are decision-support materials and do not replace independent legal, tax, or audit advice.",
      ],
    },
    {
      title: "3. Accounts and access",
      paragraphs: [
        "Registration may require an invite or administrator approval, depending on your organization’s policy.",
        "You are responsible for keeping credentials confidential and for all activity under your account.",
        "Inactive accounts or accounts that breach these terms may be suspended or closed.",
      ],
    },
    {
      title: "4. Plans and payments",
      paragraphs: [
        "Features, project limits, collaborators, and integrations depend on your active subscription plan.",
        "Pricing, billing cycles, and commercial terms are shown on the plans page and confirmed at checkout.",
        "Non-payment may result in downgrade or feature restrictions.",
      ],
    },
    {
      title: "5. User data and content",
      paragraphs: [
        "You retain ownership of data and documents you upload (projects, budgets, reports, messages).",
        "You grant the Platform a limited license to process that content solely to provide the service, including backups and requested exports.",
        "You must not upload unlawful, defamatory, or third-party infringing content.",
      ],
    },
    {
      title: "6. Acceptable use",
      paragraphs: [
        "You must not attempt unauthorized access to other users’ data, interfere with Platform security, reverse engineer the service, or use the Platform for fraud.",
        "Project sharing must comply with applicable confidentiality agreements between parties.",
      ],
    },
    {
      title: "7. Intellectual property",
      paragraphs: [
        "The Platform brand, interface, software, and documentation belong to ViabilizA+ Africa or its licensors.",
        "These terms do not transfer those rights to you, except for use rights under your subscribed plan.",
      ],
    },
    {
      title: "8. Limitation of liability",
      paragraphs: [
        "The Platform is provided “as is”, with reasonable efforts toward availability and accuracy.",
        "To the extent permitted by applicable law, we are not liable for indirect losses, lost profits, or decisions made solely based on Platform outputs.",
      ],
    },
    {
      title: "9. Changes",
      paragraphs: [
        "We may update these terms. The current version is identified by a version ID (e.g. 2026-01) and communicated when relevant.",
        "Continued use after changes constitutes acceptance of the new version, unless law requires renewed consent.",
      ],
    },
    {
      title: "10. Governing law and contact",
      paragraphs: [
        "These terms are governed by the laws of the Republic of Angola, without prejudice to mandatory consumer protection rules where applicable.",
        "Questions about these terms: comercial@viabiliza.africa",
      ],
    },
  ],
};

export const PRIVACY_PT: LegalDocument = {
  title: "Política de Privacidade",
  subtitle: "Como tratamos os seus dados pessoais na ViabilizA+ África",
  version: "2026-01",
  lastUpdated: "Janeiro de 2026",
  sections: [
    {
      title: "1. Responsável pelo tratamento",
      paragraphs: [
        "A ViabilizA+ África actua como responsável pelo tratamento dos dados pessoais recolhidos através da Plataforma.",
        "Contacto para privacidade: comercial@viabiliza.africa",
      ],
    },
    {
      title: "2. Dados que recolhemos",
      paragraphs: [
        "Dados de registo e conta: nome, email, perfil de acesso, preferências (ex.: moeda), identificadores de autenticação (incl. Google quando utilizado).",
        "Dados de utilização: logs de acesso, acções na Plataforma, notificações, mensagens de chat e metadados de projectos.",
        "Dados de projecto: informação empresarial, financeira e documentos que o utilizador introduz voluntariamente nos estudos de viabilidade.",
        "Dados de pagamento: processados por parceiros de pagamento; não armazenamos números completos de cartão.",
      ],
    },
    {
      title: "3. Finalidades",
      paragraphs: [
        "Prestar, manter e melhorar a Plataforma; autenticar utilizadores; aplicar planos e limites contratuais.",
        "Permitir colaboração, partilha de projectos, geração de relatórios e comunicações operacionais.",
        "Cumprir obrigações legais, prevenir fraude e garantir segurança da informação.",
      ],
    },
    {
      title: "4. Base legal",
      paragraphs: [
        "Execução de contrato (prestação do serviço), consentimento (ex.: registo e termos), interesse legítimo (segurança, melhoria do produto) e cumprimento de obrigações legais.",
      ],
    },
    {
      title: "5. Partilha de dados",
      paragraphs: [
        "Dados podem ser partilhados com colaboradores autorizados no âmbito de projectos partilhados.",
        "Utilizamos fornecedores de infraestrutura (ex.: alojamento/base de dados, email, autenticação Google, pagamentos) sob contratos que exigem protecção adequada.",
        "Não vendemos dados pessoais a terceiros.",
      ],
    },
    {
      title: "6. Conservação",
      paragraphs: [
        "Conservamos dados enquanto a conta estiver activa e pelo período necessário para fins legais, contabilísticos ou de resolução de litígios.",
        "Pode solicitar eliminação sujeita a limites legais e à necessidade de manter registos de auditoria.",
      ],
    },
    {
      title: "7. Segurança",
      paragraphs: [
        "Aplicamos medidas técnicas e organizativas razoáveis: controlo de acesso por perfis, registo de actividade, comunicação encriptada (HTTPS) e segregação de ambientes.",
        "Nenhum sistema é 100% seguro; reporte incidentes suspeitos através do contacto indicado.",
      ],
    },
    {
      title: "8. Os seus direitos",
      paragraphs: [
        "Pode solicitar acesso, rectificação, eliminação, limitação ou oposição ao tratamento, nos termos da lei aplicável.",
        "Para exercer direitos, contacte comercial@viabiliza.africa. Responderemos dentro dos prazos legais.",
      ],
    },
    {
      title: "9. Cookies e armazenamento local",
      paragraphs: [
        "Utilizamos cookies e armazenamento local essenciais para sessão, preferências de idioma/moeda e segurança.",
        "Pode gerir cookies no browser; a desactivação pode afectar funcionalidades.",
      ],
    },
    {
      title: "10. Alterações",
      paragraphs: [
        "Esta política pode ser actualizada. A versão vigente é identificada por 2026-01 e publicada nesta página.",
      ],
    },
  ],
};

export const PRIVACY_EN: LegalDocument = {
  title: "Privacy Policy",
  subtitle: "How we handle your personal data on ViabilizA+ Africa",
  version: "2026-01",
  lastUpdated: "January 2026",
  sections: [
    {
      title: "1. Data controller",
      paragraphs: [
        "ViabilizA+ Africa acts as the controller of personal data collected through the Platform.",
        "Privacy contact: comercial@viabiliza.africa",
      ],
    },
    {
      title: "2. Data we collect",
      paragraphs: [
        "Account data: name, email, access role, preferences (e.g. currency), authentication identifiers (including Google when used).",
        "Usage data: access logs, Platform actions, notifications, chat messages, and project metadata.",
        "Project data: business and financial information and documents you voluntarily upload for feasibility studies.",
        "Payment data: processed by payment partners; we do not store full card numbers.",
      ],
    },
    {
      title: "3. Purposes",
      paragraphs: [
        "Provide, maintain, and improve the Platform; authenticate users; enforce plans and contractual limits.",
        "Enable collaboration, project sharing, report generation, and operational communications.",
        "Meet legal obligations, prevent fraud, and ensure information security.",
      ],
    },
    {
      title: "4. Legal basis",
      paragraphs: [
        "Contract performance (service delivery), consent (e.g. signup and terms), legitimate interest (security, product improvement), and legal compliance.",
      ],
    },
    {
      title: "5. Data sharing",
      paragraphs: [
        "Data may be shared with authorized collaborators within shared projects.",
        "We use infrastructure providers (e.g. hosting/database, email, Google authentication, payments) under contracts requiring adequate protection.",
        "We do not sell personal data to third parties.",
      ],
    },
    {
      title: "6. Retention",
      paragraphs: [
        "We retain data while the account is active and as needed for legal, accounting, or dispute resolution purposes.",
        "You may request deletion subject to legal limits and audit record requirements.",
      ],
    },
    {
      title: "7. Security",
      paragraphs: [
        "We apply reasonable technical and organizational measures: role-based access, activity logging, encrypted communication (HTTPS), and environment segregation.",
        "No system is 100% secure; report suspected incidents using the contact above.",
      ],
    },
    {
      title: "8. Your rights",
      paragraphs: [
        "You may request access, rectification, erasure, restriction, or objection to processing under applicable law.",
        "Contact comercial@viabiliza.africa to exercise your rights. We will respond within legal timeframes.",
      ],
    },
    {
      title: "9. Cookies and local storage",
      paragraphs: [
        "We use essential cookies and local storage for session, language/currency preferences, and security.",
        "You can manage cookies in your browser; disabling them may affect functionality.",
      ],
    },
    {
      title: "10. Changes",
      paragraphs: [
        "This policy may be updated. The current version is identified as 2026-01 and published on this page.",
      ],
    },
  ],
};
