\# NextGen AI Security \& DLP Platform



An enterprise-style AI security platform built with \*\*AWS, Terraform, Amazon Bedrock, Amazon Cognito, API Gateway, Lambda, CloudWatch, and SNS\*\*.



The project demonstrates how security controls can be placed around an AI application to protect prompts, sensitive data, AI interactions, identities, and security telemetry.



\---



\## Architecture



```text

&#x20;                        USER

&#x20;                          |

&#x20;                          v

&#x20;                 +------------------+

&#x20;                 |   API GATEWAY    |

&#x20;                 |------------------|

&#x20;                 | Cognito JWT Auth |

&#x20;                 | Rate Limiting    |

&#x20;                 +--------+---------+

&#x20;                          |

&#x20;                          v

&#x20;                 +------------------+

&#x20;                 |     AI GATEWAY   |

&#x20;                 |------------------|

&#x20;                 | Request Validation|

&#x20;                 | Security Policy  |

&#x20;                 +--------+---------+

&#x20;                          |

&#x20;                          v

&#x20;                 +------------------+

&#x20;                 |      DLP         |

&#x20;                 |------------------|

&#x20;                 | Sensitive Data   |

&#x20;                 | Detection        |

&#x20;                 +--------+---------+

&#x20;                          |

&#x20;                          v

&#x20;                 +------------------+

&#x20;                 |    AI AGENT      |

&#x20;                 |------------------|

&#x20;                 | Policy Decisions |

&#x20;                 | Bedrock Invoke   |

&#x20;                 +--------+---------+

&#x20;                          |

&#x20;                          v

&#x20;                 +------------------+

&#x20;                 | AMAZON BEDROCK   |

&#x20;                 | Nova Lite Model  |

&#x20;                 +--------+---------+

&#x20;                          |

&#x20;                          v

&#x20;                 +------------------+

&#x20;                 | OUTPUT SECURITY  |

&#x20;                 |------------------|

&#x20;                 | Output Policy    |

&#x20;                 | Validation       |

&#x20;                 +--------+---------+

&#x20;                          |

&#x20;                          v

&#x20;                         USER





&#x20;       =========================================

&#x20;                 SECURITY MONITORING

&#x20;       =========================================



&#x20;             CloudWatch Logs

&#x20;                   |

&#x20;                   v

&#x20;             Security Metrics

&#x20;                   |

&#x20;                   v

&#x20;            CloudWatch Alarms

&#x20;                   |

&#x20;                   v

&#x20;                  SNS

&#x20;                   |

&#x20;                   v

&#x20;            Security Alerts

