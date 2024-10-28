static ssize_t portio_type_show(struct kobject *kobj, struct attribute *attr,
			     char *buf)
{
	struct uio_portio *portio = to_portio(kobj);
	struct uio_port *port = portio->port;
	struct portio_sysfs_entry *entry;

	entry = container_of(attr, struct portio_sysfs_entry, attr);

	if (!entry->show)
		return -EIO;

	return entry->show(port, buf);
}



static void arcmsr_hbaB_postqueue_isr(struct AdapterControlBlock *acb)
{
	uint32_t index;
	uint32_t flag_ccb;
	struct MessageUnit_B *reg = acb->pmuB;
	struct ARCMSR_CDB *pARCMSR_CDB;
	struct CommandControlBlock *pCCB;
	bool error;
	index = reg->doneq_index;
	while ((flag_ccb = reg->done_qbuffer[index]) != 0) {
		reg->done_qbuffer[index] = 0;
		pARCMSR_CDB = (struct ARCMSR_CDB *)(acb->vir2phy_offset+(flag_ccb << 5));
		pCCB = container_of(pARCMSR_CDB, struct CommandControlBlock, arcmsr_cdb);
		error = (flag_ccb & ARCMSR_CCBREPLY_FLAG_ERROR_MODE0) ? true : false;
		arcmsr_drain_donequeue(acb, pCCB, error);
		index++;
		index %= ARCMSR_MAX_HBB_POSTQUEUE;
		reg->doneq_index = index;
	}
}