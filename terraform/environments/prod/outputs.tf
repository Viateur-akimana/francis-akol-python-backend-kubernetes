output "prod_cluster_endpoint" {
  value = module.eks.cluster_endpoint
}

output "prod_rds_endpoint" {
  value = module.rds.db_host
}
